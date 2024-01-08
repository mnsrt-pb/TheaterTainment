/* The following code fixes bootstrap's truncated text's tooltip */

let titles = [];

document.addEventListener('DOMContentLoaded', function(e) {
    // Fixing tooltips START
    var tooltips = document.getElementsByClassName('my-tooltip');
    for (let i = 0, len = tooltips.length; i < len; i++){
        titles.push(tooltips[i].getAttribute('title'));
    }

    fixTooltips();
    window.addEventListener("resize", fixTooltips);
    // Fixing tooltips END

    // movies_sortby();
    document.getElementById('sortby').addEventListener("change", function(){
        var url=this.value;
        window.open(url, '_self')
    });
});


// Shows toottips only for movies whose titles were ellipsed
function fixTooltips()
{
    function checkEllipsis(el){
        const styles = getComputedStyle(el);
        const widthEl = parseFloat(styles.width);
        const ctx = document.createElement('canvas').getContext('2d');
        ctx.font = `${styles.fontSize} ${styles.fontFamily}`;
        const text = ctx.measureText(el.innerText);
        
        let extra = 0;
        extra += parseFloat(styles.getPropertyValue('border-left-width'));
        extra += parseFloat(styles.getPropertyValue('border-right-width'));
        extra += parseFloat(styles.getPropertyValue('padding-left'));
        extra += parseFloat(styles.getPropertyValue('padding-right'));
        return text.width > (widthEl - extra);
    } // https://stackoverflow.com/questions/7738117/html-text-overflow-ellipsis-detection

    let hasEllipses = [];

    var items = document.getElementsByClassName('text-truncate');
    for (let i = 0, len = items.length; i < len; i++){  
        if (!checkEllipsis(items[i])){
            hasEllipses.push(i);
        }
    }

    var tooltips = document.getElementsByClassName('my-tooltip');
    for (let i = 0, len = tooltips.length; i < len; i++){
        if (hasEllipses.includes(i)){
            tooltips[i].setAttribute('title', '');
        }
        else {
            tooltips[i].setAttribute('title', titles[i])
        }
    }
}

