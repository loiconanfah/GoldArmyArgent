const https = require('https');
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, 'src', 'assets', 'lottie');
if (!fs.existsSync(dir)){
    fs.mkdirSync(dir, { recursive: true });
}

const lotties = [
    { name: 'rocket.json', url: 'https://lottie.host/81b2a95c-3074-45fb-8db5-05e8105777bd/v8yT7sRjJ7.json' },
    { name: 'scan.json', url: 'https://lottie.host/762d1ea2-5cb0-40e1-88c9-4a005085e683/C5xM31I8E6.json' },
    { name: 'document.json', url: 'https://lottie.host/241d3cc2-58e6-42bb-90ad-5a3d0ae8a6a6/y16z02pG9G.json' },
    { name: 'success.json', url: 'https://lottie.host/b4fbe48e-f6f7-4a09-bb4b-e85fe56b62ff/P2y8vBxXb0.json' }
];

lotties.forEach(({name, url}) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
            try {
                fs.writeFileSync(path.join(dir, name), data);
                console.log(`Success: ${name}`);
            } catch (e) {
                console.error(`Failed parsing ${name}`, e);
            }
        });
    }).on('error', err => console.error(err));
});
