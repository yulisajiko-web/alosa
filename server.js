const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Render portni o'zi beradi, bo'lmasa 3000 ni oladi
const PORT = process.env.PORT || 3000;

// API Kalitni Render Environment Variables dan olamiz
const API_KEY = process.env.API_KEY; 

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
            // Agar body bo'sh bo'lsa xato bermasligi uchun try-catch
            try {
                const { message } = JSON.parse(body);
                const data = JSON.stringify({
                    messages: [{ role: 'user', content: message }],
                    model: 'openai', 
                    jsonMode: false
                });

                const options = {
                    hostname: 'text.pollinations.ai',
                    path: '/',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${API_KEY}`
                    }
                };

                const apiReq = https.request(options, (apiRes) => {
                    res.writeHead(apiRes.statusCode, { 'Content-Type': 'text/plain' });
                    apiRes.pipe(res);
                });

                apiReq.on('error', (e) => {
                    res.writeHead(500); res.end(e.message);
                });

                apiReq.write(data);
                apiReq.end();
            } catch (e) {
                res.writeHead(400); res.end("Bad Request");
            }
        });
        return;
    }

    // ---------------------------------------------------------
    // 2. RASM (IMAGE) UCHUN API
    // ---------------------------------------------------------
    if (req.url.startsWith('/api/image')) {
        const queryObject = url.parse(req.url, true).query;
        const prompt = queryObject.prompt;

        if (!prompt) {
            res.writeHead(400); res.end('No prompt provided'); return;
        }

        const model = 'nanobanana-pro'; 
        const seed = Math.floor(Math.random() * 1000000);
        const targetUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1024&height=1024&model=${model}&nologo=true&seed=${seed}&private=true`;

        const options = {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        };

        https.get(targetUrl, options, (proxyRes) => {
            if (proxyRes.statusCode === 200) {
                res.writeHead(200, { 'Content-Type': 'image/jpeg' });
                proxyRes.pipe(res);
            } else if (proxyRes.headers.location) {
                https.get(proxyRes.headers.location, (redirRes) => {
                    res.writeHead(200, { 'Content-Type': 'image/jpeg' });
                    redirRes.pipe(res);
                });
            } else {
                res.writeHead(500); res.end('Error generating image');
            }
        }).on('error', (e) => {
            res.writeHead(500); res.end(e.message);
        });
        return;
    }

    // ---------------------------------------------------------
    // 3. HTML FAYLLARNI OCHISH
    // ---------------------------------------------------------
    // Agar fayl nomi rasm.html bo'lsa, shuni ochamiz, bo'lmasa index.html
    let fileName = req.url === '/' ? 'index.html' : req.url;
    
    // Agar sizda fayl nomi rasm.html bo'lsa, pastdagi qatorni ochib qo'ying:
    // if (req.url === '/') fileName = 'rasm.html';

    let filePath = path.join(__dirname, fileName);
    const ext = path.extname(filePath).toLowerCase();
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

    fs.readFile(filePath, (err, content) => {
        if (err) { 
            // Agar fayl topilmasa 404 qaytaramiz
            res.writeHead(404); res.end('File not found'); 
        } 
        else { 
            res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain' }); 
            res.end(content); 
        }
    });
});

// SERVERNI FAQAT SHU YERDA, BIR MARTA ISHGA TUSHIRAMIZ:
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
