/**
 * Barrel file for all CV PDF templates.
 * To add a new template: create a new file, export a CvTemplate, and add it here.
 */
export type { CvTemplate, CvData, ParsedAudit } from './types';
export { templateGoldArmy }   from './template1_goldarmy';
export { templateMinimaliste } from './template2_minimaliste';
export { templateExecutive }  from './template3_executive';
export { templateCreatif }    from './template4_creatif';
export { templateClassique }  from './template5_classique';

import { templateGoldArmy }    from './template1_goldarmy';
import { templateMinimaliste } from './template2_minimaliste';
import { templateExecutive }   from './template3_executive';
import { templateCreatif }     from './template4_creatif';
import { templateClassique }   from './template5_classique';
import { CvTemplate } from './types';

export const CV_TEMPLATES: CvTemplate[] = [
  templateGoldArmy,
  templateMinimaliste,
  templateExecutive,
  templateCreatif,
  templateClassique,
];
