const fs = require('fs');
const frPath = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/fr.json';
const enPath = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/i18n/locales/en.json';

try {
    let frData = JSON.parse(fs.readFileSync(frPath, 'utf8'));
    frData.dashboard = {
        show_tasks: "Voir mes tâches",
        need_help: "Besoin d'aide ?",
        ask_anything: "Demandez-moi n'importe quoi !",
        smart_score: "Smart score",
        applications: "Candidatures",
        interviews: "Entretiens",
        network: "Contacts",
        total_opportunities: "Total Opportunités",
        interviews_chart: "Entretiens"
    };
    fs.writeFileSync(frPath, JSON.stringify(frData, null, 4));
    console.log("Updated fr.json");
    
    let enData = JSON.parse(fs.readFileSync(enPath, 'utf8'));
    enData.dashboard = {
        show_tasks: "Show my Tasks",
        need_help: "Hey, Need help?",
        ask_anything: "Just ask me anything!",
        smart_score: "Smart score",
        applications: "Applications",
        interviews: "Interviews",
        network: "Network",
        total_opportunities: "Total Opportunities",
        interviews_chart: "Interviews"
    };
    fs.writeFileSync(enPath, JSON.stringify(enData, null, 4));
    console.log("Updated en.json");
} catch (e) {
    console.error(e);
}
