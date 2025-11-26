Ü.const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');

const app = express();
const PORT = 3000;

app.use(cors());

let browser = null;

// Keep browser open to save time
async function getBrowser() {
    if (!browser) {
        browser = await puppeteer.launch({
            headless: "new",
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    }
    return browser;
}

app.get('/api/matches', async (req, res) => {
    console.log('Received request for matches...');
    try {
        const browser = await getBrowser();
        const page = await browser.newPage();

        // Block images and fonts to speed up
        await page.setRequestInterception(true);
        page.on('request', (req) => {
            if (['image', 'stylesheet', 'font'].includes(req.resourceType())) {
                req.abort();
            } else {
                req.continue();
            }
        });

        console.log('Navigating to Tippmix...');
        // Go to Table Tennis section directly
        await page.goto('https://www.tippmix.hu/sport/asztalitenisz', { waitUntil: 'networkidle2', timeout: 60000 });

        // Check if there are matches
        const noResults = await page.$('.no-results-selector-if-known'); // Placeholder, need to check actual "No results" element if possible, or just try to scrape

        // Wait for potential content load
        await new Promise(r => setTimeout(r, 2000));

        console.log('Scraping data...');
        const matches = await page.evaluate(() => {
            const results = [];
            // Select all match containers (using the structure found in research: a.ng-scope)
            const matchElements = document.querySelectorAll('a.ng-scope');

            matchElements.forEach(el => {
                try {
                    // Extract Time
                    const timeEl = el.querySelector('span.event-time'); // Class might need adjustment based on exact DOM
                    // Fallback to generic span if specific class not found, based on research:
                    // Time was in a span, often first or second. 
                    // Let's try to find text that looks like a date/time.

                    const spans = Array.from(el.querySelectorAll('span'));
                    const timeSpan = spans.find(s => s.textContent.match(/\d{2}\.\d{2}\.\s\d{2}:\d{2}/));
                    const time = timeSpan ? timeSpan.textContent.trim() : 'N/A';

                    // Extract Players
                    // Usually the longest text in spans, or specifically styled
                    // Based on research: "Penarol Montevideo - Nacional Montevideo" was in a span.
                    const nameSpan = spans.find(s => s.textContent.includes(' - ') && !s.textContent.includes('1X2'));
                    const nameText = nameSpan ? nameSpan.textContent.trim() : null;

                    if (nameText && time !== 'N/A') {
                        const [playerA, playerB] = nameText.split(' - ').map(s => s.trim());

                        // Extract Odds
                        // Odds are in buttons following the link, but usually siblings or children of a container.
                        // In the research, they were siblings or close by. 
                        // Actually, the structure was: a.ng-scope (link) ... button.btn-odds
                        // We need to find the parent of 'el' and look for subsequent buttons?
                        // Or maybe 'el' wraps everything?
                        // Research said: "The link a.ng-scope seems to be the main element... with odds buttons following it."

                        // Let's look at the parent's children to find the odds buttons associated with this match.
                        // This is tricky without a clear container.
                        // Heuristic: The buttons immediately following the 'a' tag.

                        const parent = el.parentElement; // The container holding the 'a' and buttons?
                        // If they are siblings:
                        let sibling = el.nextElementSibling;
                        const odds = {};

                        // Collect next few buttons
                        let safety = 0;
                        while (sibling && sibling.tagName === 'BUTTON' && sibling.classList.contains('btn-odds') && safety < 5) {
                            const marketDiv = sibling.querySelector('div'); // e.g. "H", "V"
                            const valueSpan = sibling.querySelector('span'); // e.g. "1.50"

                            if (marketDiv && valueSpan) {
                                const market = marketDiv.textContent.trim();
                                const value = parseFloat(valueSpan.textContent.replace(',', '.'));
                                odds[market] = value;
                            }
                            sibling = sibling.nextElementSibling;
                            safety++;
                        }

                        results.push({
                            time,
                            playerA,
                            playerB,
                            odds
                        });
                    }
                } catch (err) {
                    // specific match scrape failed
                }
            });
            return results;
        });

        console.log(`Found ${matches.length} matches.`);
        await page.close();
        res.json({ success: true, matches });

    } catch (error) {
        console.error('Scraping failed:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Proxy server running on http://localhost:${PORT}`);
});
Ü.*cascade082)file:///c:/Users/Tomi/PR%C3%B3ba/proxy.js