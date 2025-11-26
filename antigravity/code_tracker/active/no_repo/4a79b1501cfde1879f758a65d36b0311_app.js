±%document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

const App = {
    init: function () {
        this.cacheDOM();
        this.bindEvents();
        this.loadDashboard();
    },

    cacheDOM: function () {
        this.matchesList = document.getElementById('matchesList');
        this.activeMatchesCount = document.getElementById('activeMatchesCount');
        this.strongSignalsCount = document.getElementById('strongSignalsCount');
        this.refreshBtn = document.getElementById('refreshBtn');
    },

    bindEvents: function () {
        this.refreshBtn.addEventListener('click', () => {
            this.loadDashboard();
        });
    },

    loadDashboard: function () {
        // Show loading state
        this.matchesList.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>M√©rk≈ëz√©sek elemz√©se...</p>
            </div>
        `;

        // Simulate network delay for realism
        setTimeout(() => {
            const matches = window.DataFetcher.getMatches();
            this.renderMatches(matches);
        }, 800);
    },

    renderMatches: function (matches) {
        this.matchesList.innerHTML = '';
        let strongSignals = 0;

        matches.forEach(match => {
            // Calculate Probability
            if (result.isFlow) badgesHtml += `<span class="badge flow">FLOW üî•</span>`;

            // Determine probability bar width and color
            // Always show Player A's perspective for the bar, but color it based on who is favored
            const barWidth = result.probA;

            card.innerHTML = `
                <div class="match-header">
                    <span class="time">${match.time}</span>
                    <span class="league">Liga Pro (CZE)</span>
                </div>
                
                <div class="match-players">
                    <div class="player">
                        <span class="player-name">${match.playerA.name}</span>
                        <span class="player-rating">Rating: ${match.playerA.rating}</span>
                        <div class="player-form">
                            <small>${match.playerA.dailyWins}W / ${match.playerA.dailyLosses}L</small>
                        </div>
                    </div>
                    <span class="vs">VS</span>
                    <div class="player">
                        <span class="player-name">${match.playerB.name}</span>
                        <span class="player-rating">Rating: ${match.playerB.rating}</span>
                        <div class="player-form">
                            <small>${match.playerB.dailyWins}W / ${match.playerB.dailyLosses}L</small>
                        </div>
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="probability-bar-container">
                        <div class="probability-bar" style="width: ${barWidth}%"></div>
                    </div>
                    
                    <div class="prediction-info">
                        <div class="badges">
                            ${badgesHtml}
                        </div>
                        <div class="win-prob">
                            ${result.probA.toFixed(0)}% <span style="font-size: 0.8rem; color: #94a3b8;">es√©ly</span>
                        </div>
                    </div>
                </div>

                <div class="odds-section" style="margin-top: 1rem; display: flex; gap: 10px; justify-content: center;">
                    ${match.odds ? Object.entries(match.odds).map(([market, value]) => `
                        <div class="odd-box" style="background: #334155; padding: 5px 10px; border-radius: 4px; text-align: center;">
                            <div style="font-size: 0.7rem; color: #94a3b8;">${market}</div>
                            <div style="font-weight: bold; color: #fff;">${value.toFixed(2)}</div>
                        </div>
                    `).join('') : '<div style="color: #64748b; font-size: 0.8rem;">Nincs odds adat</div>'}
                </div>
                
                <div class="factors-list" style="margin-top: 1rem; font-size: 0.8rem; color: #94a3b8;">
                    ${result.factors.map(f => `<div>${f.name}: <span style="color: #fff;">${f.value}</span></div>`).join('')}
                </div>
            `;

            this.matchesList.appendChild(card);
        });

        // Update Stats
        this.activeMatchesCount.textContent = matches.length;
        this.strongSignalsCount.textContent = strongSignals;
    }
};
; *cascade08;a*cascade08ab *cascade08bc*cascade08cf *cascade08fm*cascade08mn *cascade08nÖ*cascade08ÖÜ *cascade08Üõ*cascade08õú *cascade08ú§*cascade08§• *cascade08•≥*cascade08≥¥ *cascade08¥æ*cascade08æ¿ *cascade08¿‘*cascade08‘€ *cascade08€Í*cascade08ÍÏ *cascade08Ï˛*cascade08˛ˇ *cascade08ˇÇ*cascade08ÇÉ *cascade08Éç*cascade08çè *cascade08è®*cascade08®™ *cascade08™¨*cascade08¨≠ *cascade08≠Ø*cascade08Ø± *cascade08±ƒ*cascade08ƒ≈ *cascade08≈÷*cascade08÷Ú *cascade08ÚÛ*cascade08ÛÙ *cascade08Ù˜*cascade08˜¯ *cascade08¯˘*cascade08˘˚ *cascade08˚˝*cascade08˝˛ *cascade08˛Ñ*cascade08Ñç *cascade08çô*cascade08ôõ *cascade08õ¢*cascade08¢£ *cascade08£ß*cascade08ß© *cascade08©¨*cascade08¨≠ *cascade08≠≈*cascade08≈∆ *cascade08∆À*cascade08ÀÃ *cascade08Ã“*cascade08“” *cascade08”‘*cascade08‘’ *cascade08’€*cascade08€ﬁ *cascade08ﬁÈ*cascade08ÈÍ *cascade08ÍÎ*cascade08ÎÏ *cascade08ÏÙ*cascade08Ùı *cascade08ı˚*cascade08˚¸ *cascade08¸Ñ*cascade08ÑÜ *cascade08Üé*cascade08éè *cascade08èò*cascade08òô *cascade08ô¢*cascade08¢£ *cascade08£ß*cascade08ß® *cascade08®≤*cascade08≤¥ *cascade08¥µ*cascade08µ∑ *cascade08∑Ω*cascade08Ωø *cascade08øÕ*cascade08ÕŒ *cascade08Œﬂ*cascade08ﬂ‡ *cascade08‡‰*cascade08‰Â *cascade08ÂÏ*cascade08ÏÓ *cascade08ÓÚ*cascade08ÚÙ *cascade08Ùı*cascade08ı¯ *cascade08¯ï*cascade08ïñ *cascade08ñó*cascade08óò *cascade08òÃ*cascade08ÃŒ *cascade08ŒÌ*cascade08ÌÔ *cascade08ÔÚ*cascade08Úı *cascade08ı˙*cascade08˙Ä *cascade08Ä±*cascade08±≤ *cascade08≤∆*cascade08∆… *cascade08…ﬂ*cascade08ﬂ‡ *cascade08‡È*cascade08ÈÎ *cascade08Îú*cascade08úù *cascade08ù§*cascade08§• *cascade08•‡*cascade08‡‚ *cascade08‚Â*cascade08ÂÊ *cascade08ÊÚ*cascade08ÚÛ *cascade08Ûà*cascade08àâ *cascade08âå*cascade08åç *cascade08çè*cascade08èê *cascade08êì*cascade08ìï *cascade08ïñ*cascade08ñó *cascade08ó®*cascade08®© *cascade08©±*cascade08±≤ *cascade08≤≥*cascade08≥¥ *cascade08¥Ω*cascade08Ω¿ *cascade08¿¬*cascade08¬√ *cascade08√”*cascade08”’ *cascade08’Ë*cascade08ËÈ *cascade08ÈÒ*cascade08ÒÛ *cascade08Û¯*cascade08¯˘ *cascade08˘£	*cascade08£	§	 *cascade08§	©	*cascade08©	´	 *cascade08´	≠	*cascade08≠	Æ	 *cascade08Æ	µ	*cascade08µ	∑	 *cascade08∑	∏	*cascade08∏	π	 *cascade08π	∫	*cascade08∫	ª	 *cascade08ª	–	*cascade08–	—	 *cascade08—	Â	*cascade08Â	Ê	 *cascade08Ê	Ì	*cascade08Ì	Ó	 *cascade08Ó	¸	*cascade08¸	˝	 *cascade08˝	˛	*cascade08˛	ˇ	 *cascade08ˇ	Ä
*cascade08Ä
Ç
 *cascade08Ç
â
*cascade08â
ä
 *cascade08ä
é
*cascade08é
ó
 *cascade08ó
√
*cascade08√
∆
 *cascade08∆
«
*cascade08«
»
 *cascade08»
Ã
*cascade08Ã
Œ
 *cascade08Œ
œ
*cascade08œ
–
 *cascade08–
“
*cascade08“
”
 *cascade08”
÷
*cascade08÷
◊
 *cascade08◊
€
*cascade08€
›
 *cascade08›
Â
*cascade08Â
Í
 *cascade08Í
Û
*cascade08Û
Ù
 *cascade08Ù
˝
*cascade08˝
ˇ
 *cascade08ˇ
ö*cascade08öõ *cascade08õú*cascade08úù *cascade08ù•*cascade08•¶ *cascade08¶Ø*cascade08Ø∞ *cascade08∞À*cascade08ÀÕ *cascade08Õ–*cascade08–“ *cascade08“‘*cascade08‘’ *cascade08’⁄*cascade08⁄‹ *cascade08‹‚*cascade08‚„ *cascade08„Ë*cascade08ËÈ *cascade08ÈÏ*cascade08ÏÌ *cascade08ÌÚ*cascade08ÚÉ *cascade08Éå*cascade08åç *cascade08çé*cascade08éè *cascade08èë*cascade08ëí *cascade08í†*cascade08†¶ *cascade08¶∑*cascade08∑∏ *cascade08∏π*cascade08π∫ *cascade08∫¡*cascade08¡√ *cascade08√Œ*cascade08Œ— *cascade08—‘*cascade08‘’ *cascade08’Ê*cascade08ÊÁ *cascade08ÁÍ*cascade08ÍÎ *cascade08ÎÏ*cascade08ÏÌ *cascade08Ì˙*cascade08˙˚ *cascade08˚Ö*cascade08Öì *cascade08ìô*cascade08ôö *cascade08ö†*cascade08†° *cascade08°π*cascade08π∫ *cascade08∫ø*cascade08ø¿ *cascade08¿ƒ*cascade08ƒ≈ *cascade08≈∆*cascade08∆» *cascade08»’*cascade08’◊ *cascade08◊Ì*cascade08ÌÚ *cascade08Úı*cascade08ıˆ *cascade08ˆ˜*cascade08˜¯ *cascade08¯¸*cascade08¸˛ *cascade08˛ˇ*cascade08ˇÄ *cascade08ÄÇ*cascade08ÇÑ *cascade08ÑÖ*cascade08ÖÜ *cascade08Üé*cascade08éê *cascade08êì*cascade08ìü *cascade08ü•*cascade08•¶ *cascade08¶ß*cascade08ß® *cascade08®©*cascade08©Ø *cascade08Øπ*cascade08πª *cascade08ªø*cascade08ø¡ *cascade08¡¬*cascade08¬√ *cascade08√À*cascade08ÀÃ *cascade08Ã„*cascade08„Â *cascade08ÂÊ*cascade08ÊË *cascade08Ë¯*cascade08¯á *cascade08áã*cascade08ãå *cascade08åé*cascade08éê *cascade08êò*cascade08òô *cascade08ôΩ*cascade08Ω≈ *cascade08≈‹*cascade08‹› *cascade08›Ó*cascade08ÓÒ *cascade08Òà*cascade08àâ *cascade08âñ*cascade08ñó *cascade08óü*cascade08ü≠ *cascade08≠¿*cascade08¿¡ *cascade08¡ÿ*cascade08ÿ⁄ *cascade08⁄‰*cascade08‰Â *cascade08Âö*cascade08öü *cascade08üÂ*cascade08ÂÊ *cascade08ÊÎ*cascade08ÎÏ *cascade08Ïı*cascade08ıˆ *cascade08ˆ¯*cascade08¯˘ *cascade08˘˚*cascade08˚¸ *cascade08¸Å*cascade08ÅÇ *cascade08Ç≤*cascade08≤≥ *cascade08≥Î*cascade08ÎÏ *cascade08ÏÓ*cascade08ÓÔ *cascade08Ôö*cascade08öú *cascade08ú®*cascade08®© *cascade08©¨*cascade08¨∫ *cascade08∫ *cascade08 À *cascade08Àœ*cascade08œ– *cascade08–‰*cascade08‰Â *cascade08ÂÇ*cascade08ÇÉ *cascade08Éô*cascade08ôö *cascade08öõ*cascade08õú *cascade08ú°*cascade08°¢ *cascade08¢§*cascade08§• *cascade08•≠*cascade08≠∞ *cascade08∞¥*cascade08¥∂ *cascade08∂æ*cascade08æø *cascade08ø∆*cascade08∆« *cascade08«À*cascade08ÀÕ *cascade08Õ’*cascade08’÷ *cascade08÷ÿ*cascade08ÿ⁄ *cascade08⁄ﬂ*cascade08ﬂÎ *cascade08ÎÛ*cascade08ÛÙ *cascade08Ù˜*cascade08˜¯ *cascade08¯à*cascade08àâ *cascade08âº*cascade08ºΩ *cascade08Ω«*cascade08«» *cascade08»“*cascade08“” *cascade08”’*cascade08’÷ *cascade08÷⁄*cascade08⁄€ *cascade08€·*cascade08·‚ *cascade08‚Á*cascade08ÁË *cascade08ËÓ*cascade08ÓÔ *cascade08ÔÒ*cascade08ÒÚ *cascade08Úˆ*cascade08ˆ˜ *cascade08˜§*cascade08§¶ *cascade08¶Æ*cascade08Æ∞ *cascade08∞—*cascade08—“ *cascade08“’*cascade08’⁄ *cascade08⁄‰*cascade08‰Â *cascade08ÂÌ*cascade08ÌÔ *cascade08Ô˛*cascade08˛ˇ *cascade08ˇÇ*cascade08ÇÉ *cascade08Éã*cascade08ãå *cascade08åﬁ*cascade08ﬁﬂ *cascade08ﬂË*cascade08ËÎ *cascade08Îë*cascade08ëí *cascade08íû*cascade08ûü *cascade08ü¢*cascade08¢§ *cascade08§®*cascade08®∞ *cascade08∞Ã*cascade08Ã” *cascade08”Ì*cascade08ÌÔ *cascade08Ôù*cascade08ù£ *cascade08£Ø*cascade08Ø∞ *cascade08∞¬*cascade08¬√ *cascade08√Õ*cascade08ÕŒ *cascade08Œ⁄*cascade08⁄€ *cascade08€‡*cascade08‡· *cascade08·Í*cascade08ÍÌ *cascade08ÌÓ*cascade08ÓÔ *cascade08Ô¯*cascade08¯˙ *cascade08˙à*cascade08àä *cascade08äï*cascade08ïõ *cascade08õ≤*cascade08≤≥ *cascade08≥¡*cascade08¡¬ *cascade08¬Œ*cascade08Œœ *cascade08œ÷*cascade08÷◊ *cascade08◊Â*cascade08ÂÁ *cascade08ÁÎ *cascade08Î¨!*cascade08¨!º! *cascade08º!¬! *cascade08¬!–!*cascade08–!—! *cascade08—!⁄!*cascade08⁄!€! *cascade08€!Á!*cascade08Á!Ë! *cascade08Ë!Û!*cascade08Û!ı! *cascade08ı!Ç"*cascade08Ç"É" *cascade08É"ç"*cascade08ç"é" *cascade08é"û"*cascade08û"ü" *cascade08ü"¿"*cascade08¿"¬" *cascade08¬"≈"*cascade08≈"∆" *cascade08∆"«"*cascade08«"À" *cascade08À"‘"*cascade08‘"’" *cascade08’"ÿ"*cascade08ÿ"Ÿ" *cascade08Ÿ"ﬂ"*cascade08ﬂ"‡" *cascade08‡"È"*cascade08È"Í" *cascade08Í"Ô"*cascade08Ô"" *cascade08"Û"*cascade08Û"Ù" *cascade08Ù"ı"*cascade08ı"¯" *cascade08¯"ç#*cascade08ç#é# *cascade08é#ö#*cascade08ö#õ# *cascade08õ#ù#*cascade08ù#†# *cascade08†#¢#*cascade08¢#£# *cascade08£#À#*cascade08À#Œ# *cascade08Œ#–#*cascade08–#’# *cascade08’#ﬁ#*cascade08ﬁ#ﬂ# *cascade08ﬂ#‡#*cascade08‡#·# *cascade08·#‚#*cascade08‚#‰# *cascade08‰#Ì#*cascade08Ì#Ó# *cascade08Ó##*cascade08#Ò# *cascade08Ò#Ù#*cascade08Ù#ı# *cascade08ı#˚#*cascade08˚#¸# *cascade08¸#˝#*cascade08˝#˛# *cascade08˛#°$*cascade08°$¢$ *cascade08¢$≥$*cascade08≥$¥$ *cascade08¥$µ$*cascade08µ$∑$ *cascade08∑$∏$*cascade08∏$π$ *cascade08π$Ω$*cascade08Ω$æ$ *cascade08æ$¡$*cascade08¡$¬$ *cascade08¬$Ÿ$*cascade08Ÿ$›$ *cascade08›$ﬁ$*cascade08ﬁ$ﬂ$ *cascade08ﬂ$Ú$*cascade08Ú$Û$ *cascade08Û$˘$*cascade08˘$˙$ *cascade08˙$¸$*cascade08¸$˝$ *cascade08˝$Ü%*cascade08Ü%á% *cascade08á%£%*cascade08£%¶% *cascade08¶%™%*cascade08™%´% *cascade08´%Æ%*cascade08Æ%±% *cascade082*file:///c:/Users/Tomi/PR%C3%B3ba/js/app.js