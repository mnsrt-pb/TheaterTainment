/* The following code fixes bootstrap's truncated text's tooltip */

let titles = [];

$(document).ready(function(){
    $('.movies-slick').slick({
        centerMode: true,
        slidesToShow: 5,

        autoplay: true,
        autoplaySpeed: 3000,

        responsive: [
          {
            breakpoint: 1200,
            settings: {
              slidesToShow: 3
            }
          },
          {
            breakpoint: 768,
            settings: {
              slidesToShow: 2
            }
          },
          {
            breakpoint: 480,
            settings: {
              centerMode: false,
              slidesToShow: 2
            }
          },
          {
            breakpoint: 390,
            settings: {
                centerMode: false,
                slidesToShow: 1
            }
          }
        ]
    });

    $('.dates-slick').slick({
        infinite: false,
        speed: 300,

        slidesToShow: 12,
        slidesToScroll: 12,

        responsive: [
          {
            breakpoint: 990,
            settings: {
              slidesToShow: 8,
              slidesToScroll: 8,
            }
          },
          {
            breakpoint: 769,
            settings: {
              slidesToShow: 6,
              slidesToScroll: 6
            }
          },
          {
            breakpoint: 480,
            settings: {
              slidesToShow: 4,
              slidesToScroll: 4
            }
          },
          {
            breakpoint: 390,
            settings: {
              slidesToShow: 3,
              slidesToScroll: 3
            }
          },
          {
            breakpoint: 330,
            settings: {
              slidesToShow: 2,
              slidesToScroll: 2
            }
          }
        ]
      });


    // Fixing tooltips START
    var tooltips = document.getElementsByClassName('my-tooltip');
    for (let i = 0, len = tooltips.length; i < len; i++){
        titles.push(tooltips[i].getAttribute('title'));
    }

    fixTooltips();
    window.addEventListener("resize", fixTooltips);
    // Fixing tooltips END

    select_link = document.getElementById('select-link')
    if (select_link != null){
        select_link.addEventListener("change", function(){
        var url=this.value;
        window.open(url, '_self')
        });
    }
  });


// document.addEventListener('DOMContentLoaded', function(e) {

// });


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


