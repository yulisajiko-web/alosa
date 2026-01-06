const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;

// ⚠️ POLLINATIONS SECRET KEYINGIZNI SHU YERGA QO'YING:
const API_KEY = 'sk_AV4OZzbD2EORlGdd46ABIJe2AoEchaLA'; // O'zingiznikini qo'ying

const server = http.createServer((req, res) => {
    
    // ---------------------------------------------------------
    // 1. CHAT (MATN) UCHUN API
    // ---------------------------------------------------------
    if (req.url.startsWith('/api/chat')) {
        if (req.method !== 'POST') {
            res.writeHead(405); res.end('Method Not Allowed'); return;
        }

        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            const { message } = JSON.parse(body);

            // Pollinations Text API ga so'rov
            // Model: 'openai' (GPT-4o) yoki 'claude' (Opus) tanlashingiz mumkin
            const data = JSON.stringify({
                messages: [{ role: 'user', content: message }],
                model: 'openai', // Yoki 'claude-3-opus'
                jsonMode: false
            });

            const options = {
                hostname: 'text.pollinations.ai',
                path: '/',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEY}` // Kalitni yuboramiz
                }
            };

            const apiReq = https.request(options, (apiRes) => {
                res.writeHead(apiRes.statusCode, { 'Content-Type': 'text/plain' });
                apiRes.pipe(res); // Javobni to'g'ridan-to'g'ri qaytaramiz
            });

            apiReq.on('error', (e) => {
                res.writeHead(500); res.end(e.message);
            });

            apiReq.write(data);
            apiReq.end();
        });
        return;
    }

    // ---------------------------------------------------------
    // 2. RASM (IMAGE) UCHUN API
    // ---------------------------------------------------------
    if (req.url.startsWith('/api/image')) {
        const queryObject = url.parse(req.url, true).query;
        const prompt = queryObject.prompt;

        // Modelni shu yerdan o'zgartirishingiz mumkin:
        // 'flux', 'nanobanana-pro', 'midjourney'
        const model = 'nanobanana-pro'; 
        
        // Tasodifiy seed
        const seed = Math.floor(Math.random() * 1000000);

        // URL yasaymiz
        const targetUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1024&height=1024&model=${model}&nologo=true&seed=${seed}&private=true`;

        const options = {
            headers: {
                'Authorization': `Bearer ${API_KEY}` // Kalitni yuboramiz (Limitga tushmaslik uchun)
            }
        };

        https.get(targetUrl, options, (proxyRes) => {
            if (proxyRes.statusCode === 200) {
                res.writeHead(200, { 'Content-Type': 'image/jpeg' });
                proxyRes.pipe(res);
            } else {
                // Agar rasmda redirect bo'lsa
                if (proxyRes.headers.location) {
                    https.get(proxyRes.headers.location, (redirRes) => {
                        res.writeHead(200, { 'Content-Type': 'image/jpeg' });
                        redirRes.pipe(res);
                    });
                } else {
                    res.writeHead(500); res.end('Error generating image');
                }
            }
        });
        return;
    }

    // ---------------------------------------------------------
    // 3. HTML FAYLLARNI OCHISH
    // ---------------------------------------------------------
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    const ext = path.extname(filePath).toLowerCase();
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

    fs.readFile(filePath, (err, content) => {
        if (err) { res.writeHead(404); res.end('Not Found'); } 
        else { res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain' }); res.end(content); }
    });
});

server.listen(PORT, () => {
    console.log(`🚀 AI Super App ishga tushdi: http://localhost:${PORT}`);
});