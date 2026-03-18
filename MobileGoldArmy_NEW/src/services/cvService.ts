import api from './api';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { Buffer } from 'buffer';

export interface CvUploadResult {
  success: boolean;
  text: string;
  filename: string;
}

export class CvUploadError extends Error {
  constructor(
    message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'CvUploadError';
  }
}

export const cvService = {
  /**
   * Sélectionne un fichier PDF depuis le device
   */
  async pickPdf(): Promise<DocumentPicker.DocumentPickerResult> {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        throw new CvUploadError('Sélection de fichier annulée', 'CANCELLED');
      }

      return result;
    } catch (error: any) {
      if (error instanceof CvUploadError) {
        throw error;
      }
      throw new CvUploadError(
        error.message || 'Erreur lors de la sélection du fichier',
        'PICK_ERROR'
      );
    }
  },

  /**
   * Upload un fichier PDF vers le backend et extrait le texte
   */
  async uploadCv(uri: string, filename: string): Promise<CvUploadResult> {
    try {
      // Pour React Native, FormData doit être créé différemment
      const formData = new FormData();
      
      // Sur React Native, on passe directement l'objet avec uri, name, type
      // Note: uri doit être un chemin local (file://) ou un URI de document picker
      formData.append('file', {
        uri,
        name: filename || 'cv.pdf',
        type: 'application/pdf',
      } as any);

      // Appel API
      // Axios détecte automatiquement FormData et définit les headers appropriés
      // Ne pas définir Content-Type manuellement, axios le fera avec le boundary
      const response = await api.post('/api/parse-pdf', formData);

      const data = response.data as { status: string; text?: string };

      if (data.status !== 'success' || !data.text) {
        throw new CvUploadError('Erreur lors de l\'extraction du texte du PDF');
      }

      return {
        success: true,
        text: data.text,
        filename: filename || 'cv.pdf',
      };
    } catch (error: any) {
      if (error instanceof CvUploadError) {
        throw error;
      }

      // Gestion des erreurs HTTP
      if (error.response) {
        const message = error.response.data?.detail || error.response.data?.message || 'Erreur serveur';
        throw new CvUploadError(message, 'SERVER_ERROR');
      }

      if (error.request) {
        throw new CvUploadError(
          'Erreur de connexion. Vérifie ta connexion internet.',
          'NETWORK_ERROR'
        );
      }

      throw new CvUploadError(
        error.message || 'Erreur inconnue lors de l\'upload',
        'UNKNOWN_ERROR'
      );
    }
  },

  /**
   * Sélectionne et upload un CV en une seule opération
   */
  async pickAndUploadCv(): Promise<CvUploadResult> {
    const pickResult = await this.pickPdf();
    
    if (pickResult.canceled || !pickResult.assets || pickResult.assets.length === 0) {
      throw new CvUploadError('Aucun fichier sélectionné', 'CANCELLED');
    }

    const asset = pickResult.assets[0];
    return await this.uploadCv(asset.uri, asset.name || 'cv.pdf');
  },

  /**
   * Génère un PDF premium via le backend
   */
  async generateCvPdf(cvData: any, themeId: string = 'goldarmy'): Promise<string> {
    try {
      const response = await api.post('/api/generate-cv-pdf', {
        cv_json: cvData,
        theme_id: themeId,
        filename: 'CV_GoldArmy_Optimise.pdf'
      }, {
        responseType: 'arraybuffer',
        headers: {
          'Accept': 'application/pdf'
        }
      });

      // Convertir ArrayBuffer en Base64
      const base64 = Buffer.from(response.data, 'binary').toString('base64');
      
      // Sauvegarder dans le cache local
      const fileUri = FileSystem.cacheDirectory + 'CV_GoldArmy.pdf';
      await FileSystem.writeAsStringAsync(fileUri, base64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      return fileUri;
    } catch (error: any) {
      console.error('[cvService] Error generating PDF:', error);
      throw new Error("Erreur lors de la génération du PDF côté serveur.");
    }
  }
};
