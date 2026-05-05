const fs = require('fs');
const frPath = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/fr.json';
const enPath = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/en.json';

try {
    let frData = JSON.parse(fs.readFileSync(frPath, 'utf8'));
    frData.opportunities = {
        ...frData.opportunities,
        tagline: "Radar Actif",
        title_sniper: "Sniper",
        title_recruitment: "Recrutement.",
        description: "Scraping intelligent du marché en temps réel et matching contextuel avec votre profil.",
        filters: {
            all: "Toutes les pertinentes",
            internships: "Stages",
            juniors: "Juniors",
            score_80: "Score > 80%"
        },
        max_results: "Résultats max:",
        search_placeholder: "Ex: Stage Ingénieur Logiciel...",
        location_placeholder: "Localisation (ex: Montréal, QC)",
        attach_cv: "Joindre CV",
        launch_button: "Lancer Sniper",
        no_opportunities: "Aucune opportunité détectée",
        no_opportunities_desc: "Renseignez vos critères de recherche ci-dessus pour lancer le Sniper."
    };
    fs.writeFileSync(frPath, JSON.stringify(frData, null, 4));
    console.log("Updated fr.json");
    
    let enData = JSON.parse(fs.readFileSync(enPath, 'utf8'));
    enData.opportunities = {
        ...enData.opportunities,
        tagline: "Radar Active",
        title_sniper: "Sniper",
        title_recruitment: "Recruitment.",
        description: "Intelligent real-time market scraping and contextual matching with your profile.",
        filters: {
            all: "All Relevant",
            internships: "Internships",
            juniors: "Juniors",
            score_80: "Score > 80%"
        },
        max_results: "Max Results:",
        search_placeholder: "Ex: Software Engineer Intern...",
        location_placeholder: "Location (e.g. Montreal, QC)",
        attach_cv: "Attach CV",
        launch_button: "Launch Sniper",
        no_opportunities: "No opportunities detected",
        no_opportunities_desc: "Fill in your search criteria above to launch the Sniper."
    };
    fs.writeFileSync(enPath, JSON.stringify(enData, null, 4));
    console.log("Updated en.json");
} catch (e) {
    console.error(e);
}
