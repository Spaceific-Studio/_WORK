(async function() {
    const rucniNazevNormy = ""; 
    console.log("🚀 STARTUJE PRŮBĚŽNÝ SBĚR A STŘÍDAVÉ STAHOVÁNÍ...");

    const findScrollable = () => {
        const all = document.querySelectorAll('*');
        for (let el of all) {
            if (el.scrollHeight > el.clientHeight && el.clientHeight > 0 &&
                (window.getComputedStyle(el).overflowY === 'auto' || 
                 window.getComputedStyle(el).overflowY === 'scroll')) {
                return el;
            }
        }
        return window;
    };

    const scroller = findScrollable();
    const downloadedUrls = new Set(); // Sledujeme, co už jsme stáhli, abychom nestahovali duplikáty
    let currentPos = 0;
    let pageCounter = 1;

    // Funkce pro okamžité stažení souboru
    const downloadNow = (url, index) => {
        const link = document.createElement('a');
        link.href = url;
        link.download = `${rucniNazevNormy}""${String(index).padStart(3, '0')}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // 1. Skok na začátek a delší klid na načtení první strany
    scroller.scrollTo(0, 0);
    await new Promise(r => setTimeout(r, 2000)); 

    while (true) {
        // 2. Najdeme obrázky na aktuální pozici
        const elements = document.querySelectorAll('img, div');
        elements.forEach(el => {
            let url = "";
            try {
                if (el.tagName === 'IMG') {
                    url = el.src;
                } else {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none' && bg.includes('url')) {
                        url = bg.match(/url\(["']?([^"']+)["']?\)/)[1];
                    }
                }
            } catch(e) {}
            
            // Pokud je to validní URL a ještě jsme ho nestáhli
            if (url && url.length > 30 && !downloadedUrls.has(url)) {
                // Filtrujeme podle velikosti (odstraní miniatury, pokud začátek stále chybí, snižte 400 na 100)
                if (el.offsetWidth > 300 || el.naturalWidth > 150) {
                    console.log(`✅ Stahuji novou stranu: ${pageCounter}`);
                    downloadNow(url, pageCounter);
                    downloadedUrls.add(url);
                    pageCounter++;
                }
            }
        });

        // 3. Posun dolů
        const step = (scroller === window ? window.innerHeight : scroller.clientHeight) * 0.6;
        currentPos += step;
        scroller.scrollTo(0, currentPos);

        // Pauza, aby se stihla načíst další várka a disk stíhal zapisovat
        await new Promise(r => setTimeout(r, 300)); 

        let newHeight = scroller === window ? document.documentElement.scrollHeight : scroller.scrollHeight;
        if (currentPos >= newHeight) break;
    }

    console.log(`🏁 Hotovo. Celkem staženo ${pageCounter - 1} stran.`);
    alert(`Proces dokončen. Celkem staženo: ${pageCounter - 1} stran.`);
})();