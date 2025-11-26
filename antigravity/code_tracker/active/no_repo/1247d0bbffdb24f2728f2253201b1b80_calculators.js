≈window.Calculators = {
    /**
     * Calculates the winning probability for Player A against Player B
     * based on Rating, H2H history, and Daily Form.
     * 
     * @param {Object} playerA - { name, rating, dailyWins, dailyLosses }
     * @param {Object} playerB - { name, rating, dailyWins, dailyLosses }
     * @param {Object} h2h - { aWins, bWins, totalMatches } (Last 10 matches recommended)
     * @returns {Object} - { probA, probB, factors, isMumus, isFlow }
     */
    calculateProbability: function (playerA, playerB, h2h) {
        let baseProb = 50;
        let factors = [];

        // 1. Rating Difference
        // Rule: +1% for every 10 points difference
        const ratingDiff = playerA.rating - playerB.rating;
        const ratingBonus = Math.round(ratingDiff / 10);
        baseProb += ratingBonus;
        if (ratingBonus !== 0) {
            factors.push({
                name: 'Rating El≈ëny',
                value: ratingBonus > 0 ? `+${ratingBonus}%` : `${ratingBonus}%`,
                desc: `${Math.abs(ratingDiff)} pont k√ºl√∂nbs√©g`
            });
        }

        // 2. H2H Dominance (Mumus Effect)
        // Rule: If won 7 out of last 10 (70%+), add 10-15%
        let h2hBonus = 0;
        let isMumus = false;

        if (h2h.totalMatches > 0) {
            const winRateA = h2h.aWins / h2h.totalMatches;

            if (winRateA >= 0.7) {
                h2hBonus = 15; // Strong dominance
                isMumus = true; // A is Mumus for B
                factors.push({ name: 'H2H Dominancia', value: '+15%', desc: 'Mumus effektus!' });
            } else if (winRateA >= 0.6) {
                h2hBonus = 8;
                factors.push({ name: 'H2H F√∂l√©ny', value: '+8%', desc: 'Stabil f√∂l√©ny' });
            } else if (winRateA <= 0.3) {
                h2hBonus = -15; // B is Mumus for A
                factors.push({ name: 'H2H H√°tr√°ny', value: '-15%', desc: 'Az ellenf√©l a Mumus' });
            } else if (winRateA <= 0.4) {
                h2hBonus = -8;
                factors.push({ name: 'H2H H√°tr√°ny', value: '-8%', desc: 'Negat√≠v m√©rleg' });
            }
        }
        baseProb += h2hBonus;

        // 3. Daily Form (Momentum / Flow)
        // Rule: Bonus for wins, penalty for losses today
        let formBonus = 0;
        let isFlow = false;

        // Simple logic: +3% per win, -3% per loss (capped at +/- 15%)
        const netWinsA = playerA.dailyWins - playerA.dailyLosses;
        formBonus += (netWinsA * 3);

        // Check for Flow State (3+ wins, 0 losses)
        if (playerA.dailyWins >= 3 && playerA.dailyLosses === 0) {
            formBonus += 5; // Extra boost for pure streak
            isFlow = true;
            factors.push({ name: 'FLOW √Ållapot', value: 'üî•', desc: 'Napi veretlens√©g (3+)' });
        }

        // Opponent form (inverse effect)
        const netWinsB = playerB.dailyWins - playerB.dailyLosses;
        formBonus -= (netWinsB * 3);

        baseProb += formBonus;
        if (formBonus !== 0) {
            factors.push({
                name: 'Napi Forma',
                value: formBonus > 0 ? `+${formBonus}%` : `${formBonus}%`,
                desc: `A: ${playerA.dailyWins}W/${playerA.dailyLosses}L vs B: ${playerB.dailyWins}W/${playerB.dailyLosses}L`
            });
        }

        // Clamp probability between 5% and 95%
        baseProb = Math.max(5, Math.min(95, baseProb));

        return {
            probA: baseProb,
            probB: 100 - baseProb,
            factors: factors,
            isMumus: isMumus, // True if Player A dominates H2H
            isFlow: isFlow    // True if Player A is in Flow
        };
    }
};
 *cascade088*cascade088: *cascade08:G*cascade08GI *cascade08IJ*cascade08JL *cascade08Lx*cascade08xy *cascade08y|*cascade08|~ *cascade08~ä*cascade08äã *cascade08ãê*cascade08êë *cascade08ëí*cascade08íì *cascade08ìò*cascade08òô *cascade08ôû*cascade08û§ *cascade08§©*cascade08©≠ *cascade08≠º*cascade08ºΩ *cascade08ΩÃ*cascade08ÃÕ *cascade08Õ‘*cascade08‘’ *cascade08’Ÿ*cascade08Ÿ€ *cascade08€Ü*cascade08Üà *cascade08à†*cascade08†° *cascade08°À*cascade08ÀÃ *cascade08ÃÔ*cascade08ÔÒ *cascade08Òì*cascade08ìî *cascade08î•*cascade08•¶ *cascade08¶∞*cascade08∞± *cascade08±≤*cascade08≤≥ *cascade08≥Ω*cascade08Ωæ *cascade08æ¿*cascade08¿¡ *cascade08¡«*cascade08«» *cascade08»—*cascade08—” *cascade08”ˆ*cascade08ˆ˜ *cascade08˜Ü*cascade08Üá *cascade08áà*cascade08àâ *cascade08âÌ*cascade08ÌÓ *cascade08ÓÙ*cascade08Ùı *cascade08ı˙*cascade08˙˚ *cascade08˚è*cascade08èë *cascade08ëù*cascade08ùû *cascade08ûß*cascade08ß© *cascade08©´*cascade08´¨ *cascade08¨¿*cascade08¿¡ *cascade08¡¬*cascade08¬√ *cascade08√À*cascade08ÀÃ *cascade08Ã÷*cascade08÷◊ *cascade08◊¸*cascade08¸˝ *cascade08˝Ö*cascade08ÖÜ *cascade08Üú*cascade08úù *cascade08ù™*cascade08™∂ *cascade08∂ÿ*cascade08ÿ‹ *cascade08‹°*cascade08°¢ *cascade08¢®*cascade08®© *cascade08©«*cascade08«… *cascade08…’*cascade08’◊ *cascade08◊Â*cascade08ÂÊ *cascade08ÊÛ*cascade08ÛÙ *cascade08Ùˆ*cascade08ˆ˜ *cascade08˜Ü*cascade08Üà *cascade08àâ*cascade08âï *cascade08ïò*cascade08òö *cascade08öõ*cascade08õú *cascade08ú≠*cascade08≠Æ *cascade08Æ˝*cascade08˝˛ *cascade08˛Ä	*cascade08Ä	Å	 *cascade08Å	¢	*cascade08¢	£	 *cascade08£	¶	*cascade08¶	ß	 *cascade08ß	´	*cascade08´	¨	 *cascade08¨	∞	*cascade08∞	≤	 *cascade08≤	∆	*cascade08∆	…	 *cascade08…	€	*cascade08€	‹	 *cascade08‹	„	*cascade08„	‰	 *cascade08‰	˜	*cascade08˜	¯	 *cascade08¯	˘	*cascade08˘	˚	 *cascade08˚	ù
*cascade08ù
û
 *cascade08û
ß
*cascade08ß
®
 *cascade08®
∆
*cascade08∆
«
 *cascade08«
 
*cascade08 
À
 *cascade08À
’
*cascade08’
◊
 *cascade08◊
Ê
*cascade08Ê
Á
 *cascade08Á
˛
*cascade08˛
Ä *cascade08ÄÜ*cascade08Üá *cascade08áà*cascade08àâ *cascade08âä*cascade08äã *cascade08ãê*cascade08ê§ *cascade08§®*cascade08®™ *cascade08™´*cascade08´¨ *cascade08¨∑*cascade08∑∏ *cascade08∏º*cascade08ºΩ *cascade08Ω¬*cascade08¬√ *cascade08√ﬂ*cascade08ﬂ‚ *cascade08‚é*cascade08éè *cascade08èí*cascade08íî *cascade08îü*cascade08ü† *cascade08†®*cascade08®© *cascade08©¨*cascade08¨≠ *cascade08≠’*cascade08’÷ *cascade08÷ˆ*cascade08ˆ˜ *cascade08˜˝*cascade08˝˛ *cascade08˛Ñ*cascade08ÑÖ *cascade08Öª*cascade08ªº *cascade08ºø*cascade08ø¿ *cascade08¿¡*cascade08¡¬ *cascade08¬ﬂ*cascade08ﬂ‰ *cascade08‰Ü*cascade08Üñ *cascade08ñó*cascade08óò *cascade08òú*cascade08úù *cascade08ùü*cascade08ü† *cascade08†Ÿ*cascade08Ÿ€ *cascade08€„*cascade08„‰ *cascade08‰¯*cascade08¯˘ *cascade08˘Ü*cascade08Üá *cascade08á†*cascade08†£ *cascade08£¶*cascade08¶ß *cascade08ß*cascade08Ò *cascade08Ò˜*cascade08˜å *cascade08åî*cascade08îï *cascade08ïñ*cascade08ñó *cascade08óú*cascade08úû *cascade08ûÆ*cascade08ÆØ *cascade08Ø∞*cascade08∞± *cascade08±ª*cascade08ªº *cascade08º‚*cascade08‚„ *cascade08„Î*cascade08ÎÏ *cascade08Ïí*cascade08íì *cascade08ì•*cascade08•© *cascade08©™*cascade08™¨ *cascade08¨“*cascade08“” *cascade08”€*cascade08€ﬁ *cascade08ﬁﬂ*cascade08ﬂ‡ *cascade08‡‚*cascade08‚„ *cascade08„Î*cascade08ÎÏ *cascade08Ïı*cascade08ıˆ *cascade08ˆ∏*cascade08∏ƒ *cascade08ƒ«*cascade08«» *cascade08»Œ*cascade08Œœ *cascade08œ–*cascade08–— *cascade08—€*cascade08€„ *cascade08„Â*cascade08ÂÊ *cascade08Êä*cascade08äã *cascade08ãè*cascade08èê *cascade08êì*cascade08ìî *cascade08î≠*cascade08≠Æ *cascade08ÆØ*cascade08Ø∞ *cascade08∞√*cascade08√ƒ *cascade08ƒ‘*cascade08‘’ *cascade08’€*cascade08€‹ *cascade08‹·*cascade08·‚ *cascade08‚Ò*cascade08ÒÚ *cascade08Ú˝*cascade08˝˛ *cascade08˛Å*cascade08ÅÇ *cascade08Ç©*cascade08©™ *cascade08™Æ*cascade08ÆØ *cascade08Ø≥*cascade08≥¥ *cascade08¥œ*cascade08œ— *cascade08—Ÿ*cascade08Ÿ⁄ *cascade08⁄Ì*cascade08ÌÓ *cascade08ÓÒ*cascade08ÒÚ *cascade08Úï*cascade08ïñ *cascade08ñò*cascade08òô *cascade08ô¨*cascade08¨≠ *cascade08≠Ä*cascade08ÄÅ *cascade08Åº*cascade08ºΩ *cascade08Ω„*cascade08„‰ *cascade08‰Ó*cascade08ÓÔ *cascade08Ô¯*cascade08¯˘ *cascade08˘Ö*cascade08Öá *cascade08áà*cascade08àâ *cascade08âã*cascade08ãå *cascade08åè*cascade08èê *cascade08êí*cascade08íñ *cascade08ñö*cascade08öõ *cascade08õú*cascade08úù *cascade08ùü*cascade08ü† *cascade08†≠*cascade08≠Æ *cascade08Æ±*cascade08±≤ *cascade08≤‘*cascade08‘’ *cascade08’·*cascade08·Â *cascade08ÂÁ*cascade08ÁÌ *cascade08Ìá*cascade08áå *cascade08åß*cascade08ß¨ *cascade08¨≤*cascade08≤≥ *cascade08≥Ω*cascade08Ωæ *cascade08æ÷*cascade08÷◊ *cascade08◊ÿ*cascade08ÿŸ *cascade08ŸÊ*cascade08Ê¯ *cascade08¯˛*cascade08˛ˇ *cascade08ˇà*cascade08àâ *cascade08âä*cascade08äã *cascade08ãå*cascade08åç *cascade08çò*cascade08òô *cascade08ôö*cascade08öõ *cascade08õ®*cascade08®© *cascade08©≈*cascade08≈∆ *cascade08∆ﬂ*cascade08ﬂ‡ *cascade08‡Ì*cascade08ÌÓ *cascade08Ó˜*cascade08˜¯ *cascade08¯Ö*cascade08ÖÜ *cascade08Üà*cascade08àâ *cascade08âû*cascade08ûü *cascade08ü†*cascade08†° *cascade08°¢*cascade08¢£ *cascade08£§*cascade08§• *cascade08•ﬁ*cascade08ﬁ‡ *cascade08‡Ë*cascade08ËÍ *cascade08ÍÓ*cascade08ÓÔ *cascade08Ô˙*cascade08˙˚ *cascade08˚ç*cascade08çë *cascade08ëò*cascade08òô *cascade08ô¢*cascade08¢£ *cascade08£∞*cascade08∞± *cascade08±∆*cascade08∆« *cascade08«‹*cascade08‹› *cascade08›‰*cascade08‰Â *cascade08ÂÌ*cascade08ÌÓ *cascade08ÓÔ*cascade08Ô *cascade08É*cascade08ÉÑ *cascade08Ñé*cascade08éú *cascade08úØ*cascade08Ø≥ *cascade08≥Ó*cascade08Ó¸ *cascade08¸¨*cascade08¨∑ *cascade08∑∏*cascade08∏≈ *cascade0822file:///c:/Users/Tomi/PR%C3%B3ba/js/calculators.js