var valid = require("card-validator");

let titles = [];

$(document).ready(function(){
  if ($('.movies-slick').slick)(
    $('.movies-slick').slick({
      centerMode: true,
      slidesToShow: 5,

      autoplay: true,
      autoplaySpeed: 2500,

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
    })
  );

  if ($('.dates-slick').slick)(
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
    })
  );

  // Fixing tooltips START
  $('.my-tooltip').map(function() {
    titles.push($(this).attr('title'));
  })

  fixTooltips();

  window.addEventListener("resize", fixTooltips);
  // Fixing tooltips END

  $('#select-link').on('change', function (){
    window.open(this.value, '_self')
  })

  $('#modal-trailer').on('show.bs.modal', function(e){
    // Modal trigger
    var trigger = $(e.relatedTarget) 
    
    // Fetch modal data
    var title = trigger.data('movie-title')
    var trailer_path = trigger.data('movie-trailer-path')
    var poster_path = trigger.data('movie-poster-path')
    var rating = trigger.data('movie-rating')
    var runtime = trigger.data('movie-runtime')

    if (runtime < 60){
      runtime = runtime + ' min'
    } else {
      runtime = Math.floor(parseInt(runtime)/60) + ' hr ' + parseInt(runtime)%60 + ' min'
    }
    // Modal
    var modal = $(this)

    // Replace data
    modal.find('#modal-iframe').attr('src', 'https://www.youtube.com/embed/'+ trailer_path + '?autoplay=1&mute=1');
    modal.find('#modal-poster').attr('src', 'https://image.tmdb.org/t/p/original' + poster_path);
    modal.find('#modal-poster').attr('alt', 'Poster for ' + title);
    modal.find('#modal-title').text(title);
    modal.find('#modal-rating').text(rating);
    modal.find('#modal-runtime').text(runtime);
  })
  
  $('.add-watchlist').each(function(){
      $(this).hover(function (){
        $(this).find('.heart').html("&#9829;")
      })
      $(this).mouseleave(function (){
        $(this).find('.heart').html("&#9825;")
      })
  })

  ticket_seat_map();
  checkout_form_control();
});


// Shows toottips only for movies whose titles were ellipsed (fixes bootstrap's truncated text's tooltip)
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

function ticket_seat_map(){
  var seats = 0
  var adult_tickets = 0
  var child_tickets = 0
  var senior_tickets = 0

  $('#modal-seat-wheelchair').on('show.bs.modal', function(e){
    // Modal trigger
    var trigger = $(e.relatedTarget)

    // Fetch modal data
    var id = trigger.data('seat-id')
    var available = trigger.data('available')

    // Replace data
    $(this).find('.modal-seat').data('seat-id', id);
    $(this).find('.modal-seat').data('available', available);
  })

  $('.modal-trigger').on('click', function(){
    if (!$(this).hasClass('selected')){
      modal_seat = $($(this).data('bs-target'))
      $($(this).data('bs-target')).modal('toggle'); 

      // Modal trigger
      trigger = $(this)

      // Fetch modal data
      var id = trigger.data('seat-id')
      var available = trigger.data('available')

      // Replace data
      modal_seat.modal().find('.modal-seat').data('seat-id', id);
      modal_seat.modal().find('.modal-seat').data('available', available);
    } else {
      id = $(this).data('seat-id')

      $('.seat').each(function(){
        if ($(this).data('seat-id') == id){
          seats = seatSelected($(this), seats);
          checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets)
        }
      })
    }
  })
  
  $('.modal-seat').on('click', function(){
    id = $(this).data('seat-id')

    $('.seat').each(function(){
      if ($(this).data('seat-id') == id){
        seats = seatSelected($(this), seats);
        checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets)
      }
    })
  })

  $('.seat').on('click', function(){
    if ($(this).data('seat-type') == 'normal'){
      seats = seatSelected($(this), seats);

      if (seats == 0){
        adult_tickets = 0
        child_tickets = 0
        senior_tickets = 0
        $('#ticket-selector-adult').text(0)
        $('#ticket-selector-child').text(0)
        $('#ticket-selector-senior').text(0)
      }

      checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets)
    }
  })

  $('.btn-inc').on('click', function(){
    curr = $('#ticket-selector-' + $(this).data('ticket-type')).text()
    $('#ticket-selector-' + $(this).data('ticket-type')).text(++curr)
    $('#' + $(this).data('ticket-type') + '-tickets').val(curr)

    if (curr == 1){
      $('#'+$(this).data('ticket-type')).find('.btn-dec').prop("disabled", false)
    }

    if ($(this).data('ticket-type') == 'adult'){
      adult_tickets = curr
    } else if ($(this).data('ticket-type') == 'child'){
      child_tickets = curr
    } else {
      senior_tickets = curr
    }
    
    checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets)
  })

  $('.btn-dec').on('click', function(){
    curr = $('#ticket-selector-' + $(this).data('ticket-type')).text()
    $('#ticket-selector-' + $(this).data('ticket-type')).text(--curr)
    $('#' + $(this).data('ticket-type') + '-tickets').val(curr)

    if (curr == 0){
      $('#'+$(this).data('ticket-type')).find('.btn-dec').prop("disabled", true)
    }

    if ($(this).data('ticket-type') == 'adult'){
      adult_tickets = curr
    } else if ($(this).data('ticket-type') == 'child'){
      child_tickets = curr
    } else {
      senior_tickets = curr
    }

    checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets)
  })
}


function checkout_form_control(){
  $('#guest-checkout').on('click', function(){
    $('#checkout-selection').prop('hidden', true)
    $('#checkout-form').prop('hidden', false)
  })

  // If user edits email field, remove is-invalid
  $('#email').on('keypress', function(){
    if ($('#email').hasClass('is-invalid')){
      $('#email-e').text('')
      $('#email').removeClass('is-invalid')
    }
  })

  /* Validate string length */
  // Check card_type and validate card
  $('#card-number').on('focusout', function(){
    number = valid.number($(this).val())
    if (number.card != null){
      if (number.card.type == 'visa' || number.card.type == 'mastercard'  || number.card.type == 'discover'){
        $('#cc_holder').removeClass('Visa')
        $('#cc_holder').removeClass('Mastercard')
        $('#cc_holder').removeClass('Discover')
        $('#cc_holder').removeClass('AmericanExpress')
        $('#cc_holder').addClass(number.card.niceType)
      } else if (number.card.type == 'american-express'){
        $('#cc_holder').removeClass('Visa')
        $('#cc_holder').removeClass('Mastercard')
        $('#cc_holder').removeClass('Discover')
        $('#cc_holder').addClass('AmericanExpress')
      }

      // Validate
      if (!($(this).val().length >= 8 && $(this).val().length <= 19)){
        $('#card-number-e').text('The Card Number field is not a valid credit card number.')
        $('#card-number').addClass('is-invalid')
      } else {
        if (number.isValid){
          $('#card-number-e').text('')
          $('#card-number').removeClass('is-invalid')
        } else {
          $('#card-number-e').text('The Card Number field is not a valid credit card number.')
          $('#card-number').addClass('is-invalid')
        }
      }
    } else {
      if ($(this).val().length == 0){
        $('#card-number-e').text('The Card Number field is required.')
        $('#card-number').addClass('is-invalid')
      } else {
        $('#card-number-e').text('The Card Number field is not a valid credit card number.')
        $('#card-number').addClass('is-invalid')
      }
    }

    if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
    || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
    && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
    && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
      if (!valid.expirationDate($('#exp-month').val() + '/' + $('#exp-year').val()).isValid){
        $('#exp-month-e').text('The Month field is invalid.')
        $('#exp-month').addClass('is-invalid')
      } else {
        $('#exp-month-e').text('')
        $('#exp-month').removeClass('is-invalid')
        $('#checkout-button').prop('hidden', false)
      }
    } else {
      $('#checkout-button').prop('hidden', true)
    }
  })

  // FIXME: After uncommenting code that disables copy/paste remove this code
  $('#card-number').on('change', function(){
    $('#card_type').val(valid.number($(this).val()).card.niceType)
  })

  $('#zip-code').on('focusout', function(){
    if ($(this).val().length == 0){
      $('#zip-code-e').text('The Billing ZIP Code field is required.')
      $('#zip-code').addClass('is-invalid')
    } else if ($(this).val().length != 5){
      $('#zip-code-e').text('The value for the Billing Zip Code field is invalid.')
      $('#zip-code').addClass('is-invalid')

    } else {
      $('#zip-code-e').text('')
      $('#zip-code').removeClass('is-invalid')
    }

    if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
    || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
    && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
    && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
      if (!valid.expirationDate($('#exp-month').val() + '/' + $('#exp-year').val()).isValid){
        $('#exp-month-e').text('The Month field is invalid.')
        $('#exp-month').addClass('is-invalid')
      } else {
        $('#exp-month-e').text('')
        $('#exp-month').removeClass('is-invalid')
        $('#checkout-button').prop('hidden', false)
      }
    } else {
      $('#checkout-button').prop('hidden', true)
    }
  })
  
  $('#sec-code').on('focusout', function(){
    if ($(this).val().length == 0){
      $('#sec-code-e').text('The Card Security Code field is required.')
      $('#sec-code').addClass('is-invalid')
    } else if (!($(this).val().length >= 3 && $(this).val().length <= 4)){
      $('#sec-code-e').text('The Card Security Code field is not a valid credit card security code.')
      $('#sec-code').addClass('is-invalid')

    } else {
      $('#sec-code-e').text('')
      $('#sec-code').removeClass('is-invalid')
    }

    if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
    || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
    && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
    && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
      if (!valid.expirationDate($('#exp-month').val() + '/' + $('#exp-year').val()).isValid){
        $('#exp-month-e').text('The Month field is invalid.')
        $('#exp-month').addClass('is-invalid')
      } else {
        $('#exp-month-e').text('')
        $('#exp-month').removeClass('is-invalid')
        $('#checkout-button').prop('hidden', false)
      }
    } else {
      $('#checkout-button').prop('hidden', true)
    }
  })

  $('#email').on('focusout', function(){
    if ($(this).val().length == 0){
      $('#email-e').text('The Email Address field is required.')
      $('#email').addClass('is-invalid')
    } else {
      $('#email-e').text('')
      $('#email').removeClass('is-invalid')
    }

    if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
    || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
    && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
    && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
      if (!valid.expirationDate($('#exp-month').val() + '/' + $('#exp-year').val()).isValid){
        $('#exp-month-e').text('The Month field is invalid.')
        $('#exp-month').addClass('is-invalid')
      } else {
        $('#exp-month-e').text('')
        $('#exp-month').removeClass('is-invalid')
        $('#checkout-button').prop('hidden', false)
      }
    } else {
      $('#checkout-button').prop('hidden', true)
    }
  })

  /* zip-code, sec-code, card-number inputs must be number keys */
  $('#card-number').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    $('#card_type').val(valid.number($(this).val()).card.niceType)
    return true; 
  })

  $('#zip-code').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    return true; 
  })

  $('#sec-code').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    return true; 
  })

  /* Validate Date */
  $('#exp-month').on('change', function(){
    if (!valid.expirationDate($(this).val() + '/' + $('#exp-year').val()).isValid){
      $('#exp-month-e').text('The Month field is invalid.')
      $('#exp-month').addClass('is-invalid')
      $('#checkout-button').prop('hidden', true)
    } else {
      $('#exp-month-e').text('')
      $('#exp-month').removeClass('is-invalid')

      if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
      || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
      && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
      && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
        $('#checkout-button').prop('hidden', false)
      } else {
        $('#checkout-button').prop('hidden', true)
      }
    }
  })

  $('#exp-year').on('change', function(){
    console.log(valid.expirationDate($('#exp-month').val() + '/' + $(this).val()).isValid)
    if (!valid.expirationDate($('#exp-month').val() + '/' + $(this).val()).isValid){
      $('#exp-month-e').text('The Month field is invalid.')
      $('#exp-month').addClass('is-invalid')
      $('#checkout-button').prop('hidden', true)
    } else {
      $('#exp-month-e').text('')
      $('#exp-month').removeClass('is-invalid')
      if (!($('#card-number').hasClass('is-invalid') || $('#zip-code').hasClass('is-invalid') 
      || $('#sec-code').hasClass('is-invalid') || ($('#email').hasClass('is-invalid')))
      && ($('#card-number').val().length != 0) && ($('#zip-code').val().length != 0) 
      && ($('#sec-code').val().length != 0) && ($('#email').val().length != 0)){
        $('#checkout-button').prop('hidden', false)
      } else {
        $('#checkout-button').prop('hidden', true)
      }
    }
  })

  /* Disable paste and copy */
  /*
  $('#card-number').on("paste", function(e) { 
    return false;
  }); 

  $('#zip-code').on("paste", function(e) { 
    return false;
  }); 
  
  $('#sec-code').on("paste", function(e) { 
    return false;
  }); 

  $('#card-number').on("copy", function(e) { 
    return false;
  }); 

  $('#zip-code').on("copy", function(e) { 
    return false;
  }); 

  $('#sec-code').on("copy", function(e) { 
    return false;
  }); 
  */
}


function checkTicketChanges(seats, adult_tickets, child_tickets, senior_tickets){
  if ($('#add-more-warning:hidden')){
    $('#add-more-warning').prop('hidden', false)
  }
  if (!$('#select-seats-button').prop('disabled')){
    $('#select-seats-button').prop('disabled', true)
  }

  tickets = adult_tickets + child_tickets + senior_tickets
  if (tickets == 0){
    $('.seat-tickets-warning-2').text('Add tickets for your selected seats to continue.')
  } else {
    $('.seat-tickets-warning-2').text('')
  }

  if (tickets < seats){
    if ((seats - tickets) == 1){
      $('.seat-tickets-warning').text('1 selected seat has no ticket.')
    } else {
      $('.seat-tickets-warning').text((seats - tickets) + ' selected seats have no tickets.')
    }
  } else if (tickets > seats){
    if ((tickets - seats) == 1){
      $('.seat-tickets-warning').text('1 ticket has no selected seat.')
    } else {
      $('.seat-tickets-warning').text((tickets - seats) + ' tickets have no selected seats.')
    }    
  } else {
    $('.seat-tickets-warning').text('')
    $('#add-more-warning').prop('hidden', true)
    if (tickets != 0 ){
      $('#select-seats-button').prop('disabled', false)
    }
  }
}


function seatSelected(t, seats){
  var seats_selected;

  if (t.data('available') == "True"){
    if (t.hasClass('selected')){
      t.removeClass('selected')

      seats_selected = $('#seats-selected').val().split(',')
      seats_selected = seats_selected.filter(e => e != t.data('seat-id'))
      $('#seats-selected').val(seats_selected.toString())

      seats -= 1;
    } else {
      t.addClass('selected')

      if ($('#seats-selected').val() == ''){
        seats_selected = []
      } else {
        seats_selected = $('#seats-selected').val().split(',')
      }
      seats_selected.push(t.data('seat-id'))
      $('#seats-selected').val(seats_selected.toString())

      seats += 1;
    }
  }

  if (seats == 0){
    $('#select-seats-form').prop("hidden", true)
    $('#select-seats-message').prop("hidden", false)
    $('#select-seats-button').prop("disabled", true)
  } else {
    if ($('#select-seats-message:visible')){
      $('#select-seats-message').prop("hidden", true)
      $('#select-seats-form').prop("hidden", false)
    }

    if (seats == 1){
      $('#tickets-amt').text(seats + ' Ticket')
    } else {
      $('#tickets-amt').text(seats + ' Tickets')
    }
  }

  return seats;
}
