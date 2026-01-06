const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Render portni o'zi beradi
const PORT = process.env.PORT || 3000;

// Render "Environment Variables" bo'limiga qo'ygan kalitingizni oladi
const API_KEY = process.env.API_KEY; 

const server = http.createServer((req, res) => {
    
    // ---------------------------------------------------------
    // 1. CHAT API (Matn yozish uchun)
    // ---------------------------------------------------------
    if (req.url.startsWith('/api/chat')) {
        if (req.method !== 'POST') {
            res.writeHead(405); res.end('Method Not Allowed'); return;
        }

        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const { message } = JSON.parse(body);
                // Pollinations ga so'rov yuborish
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
                        'Authorization': `Bearer ${API_KEY}` // Kalitni ishlatamiz
                    }
                };

                const apiReq = https.request(options, (apiRes) => {
                    res.writeHead(apiRes.statusCode, { 'Content-Type': 'text/plain' });
                    apiRes.pipe(res);
                });

                apiReq.on('error', (e) => { res.writeHead(500); res.end(e.message); });
                apiReq.write(data);
                apiReq.end();
            } catch (e) { res.writeHead(400); res.end("Bad Request"); }
        });
        return;
    }

    // ---------------------------------------------------------
    // 2. IMAGE API (Rasm chizish uchun)
    // ---------------------------------------------------------
    if (req.url.startsWith('/api/image')) {
        const queryObject = url.parse(req.url, true).query;
        const prompt = queryObject.prompt;

        if (!prompt) { res.writeHead(400); res.end('No prompt'); return; }

        // Modelni tanlash (nanobanana-pro yoki flux)
        const model = 'nanobanana-pro'; 
        const seed = Math.floor(Math.random() * 1000000);
        
        const targetUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1024&height=1024&model=${model}&nologo=true&seed=${seed}&private=true`;

        const options = {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
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
        }).on('error', (e) => { res.writeHead(500); res.end(e.message); });
        return;
    }

    // ---------------------------------------------------------
    // 3. FAYLLARNI OCHISH (ENG MUHIM QISM)
    // ---------------------------------------------------------
    
    // Agar saytga shunchaki kirsa ('/'), 'rasm.html' ni ochsin!
    let fileName = req.url === '/' ? 'rasm.html' : req.url;
    
    let filePath = path.join(__dirname, fileName);
    const ext = path.extname(filePath).toLowerCase();
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('Fayl topilmadi. rasm.html fayli borligini tekshiring.');
        } else {
            res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain' });
            res.end(content);
        }
    });
});

server.listen(PORT, () => {
    console.log(`Server ishga tushdi: ${PORT}`);
});
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
