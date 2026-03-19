/**
 * Barrel file for all CV PDF templates.
 * To add a new template: create a new file, export a CvTemplate, and add it here.
 */
export type { CvTemplate, CvData, ParsedAudit } from './types';
export { templateGoldArmy }    from './template1_goldarmy';
export { templateMinimaliste } from './template2_minimaliste';
export { templateExecutive }   from './template3_executive';
export { templateCreatif }     from './template4_creatif';
export { templateClassique }   from './template5_classique';
export { templateNeonTech }    from './template6_neon_tech';
export { templateScandinave }  from './template7_scandinave';
export { templateTimeline }    from './template8_timeline';

import { templateGoldArmy }    from './template1_goldarmy';
import { templateMinimaliste } from './template2_minimaliste';
import { templateExecutive }   from './template3_executive';
import { templateCreatif }     from './template4_creatif';
import { templateClassique }   from './template5_classique';
import { templateNeonTech }    from './template6_neon_tech';
import { templateScandinave }  from './template7_scandinave';
import { templateTimeline }    from './template8_timeline';
import { CvTemplate } from './types';

export const CV_TEMPLATES: CvTemplate[] = [
  templateGoldArmy,
  templateMinimaliste,
  templateExecutive,
  templateCreatif,
  templateClassique,
  templateNeonTech,
  templateScandinave,
  templateTimeline,
];
