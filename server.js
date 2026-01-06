const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

// RENDER UCHUN MUHIM O'ZGARISH:
const PORT = process.env.PORT || 3000; 

// API KALITNI RENDERDAN OLAMIZ:
const API_KEY = process.env.API_KEY; 

const server = http.createServer((req, res) => {
    
    // --- API QISMLARI (O'ZGARISHSIZ) ---
    if (req.url.startsWith('/api/chat')) {
        // ... (bu yerda eski chat kodingiz turaveradi)
        // Faqat API_KEY o'zgaruvchisini ishlatayotganiga ishonch hosil qiling
        return;
    }

    if (req.url.startsWith('/api/image')) {
        // ... (bu yerda eski rasm kodingiz turaveradi)
        return;
    }

    // --- FAYLLARNI OCHISH QISMI (MUHIM O'ZGARISH) ---
    
    // Agar shunchaki saytga kirsa ('/'), 'rasm.html' ni ochsin:
    let filePath = path.join(__dirname, req.url === '/' ? 'rasm.html' : req.url);
    
    const ext = path.extname(filePath).toLowerCase();
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

    fs.readFile(filePath, (err, content) => {
        if (err) { 
            res.writeHead(404); 
            res.end('Fayl topilmadi. rasm.html borligini tekshiring.'); 
        } 
        else { 
            res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain' }); 
            res.end(content); 
        }
    });
});

server.listen(PORT, () => {
    console.log(`Server ishga tushdi port: ${PORT}`);
});
server.listen(PORT, () => {
    console.log(`🚀 AI Super App ishga tushdi: http://localhost:${PORT}`);
});
