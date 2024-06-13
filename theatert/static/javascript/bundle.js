(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
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
    // ♥
    // ♡
    if ($(this).find('.heart').html() == "♡"){
      $(this).hover(function (){
        $(this).find('.heart').html("&#9829;")
      })
      $(this).mouseleave(function (){
        $(this).find('.heart').html("&#9825;")
      })
    } else {
      $(this).hover(function (){
        $(this).find('.heart').html("&#9825;")
      })
      $(this).mouseleave(function (){
        $(this).find('.heart').html("&#9829;")
      })
    }
  })

  ticket_seat_map();
  checkout_form_control();
  member_forms_control();
  account_profile_control();
});


// Shows tooltips only for movies whose titles were ellipsed (fixes bootstrap's truncated text's tooltip)
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
    $('#' + $(this).data('ticket-type') + '_tickets').val(curr)

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
    $('#' + $(this).data('ticket-type') + '_tickets').val(curr)

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
  $('.guest-email').on('keypress', function(){
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

      $("input[name=card_type]").val(number.card.niceType)

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

  $('.guest-email').on('focusout', function(){
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
    $("input[name=card_type]").val(valid.number($(this).val()).card.niceType)
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
}


function member_forms_control(){
  $('#zip_code').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    return true; 
  })
  $('#zip_code').on("paste", function(e) { 
    return false;
  });
  $('#zip_code').on("copy", function(e) { 
    return false;
  })

  $('#phone').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
      return false;
    return true; 
  })
  $('#phone').on("paste", function(e) { 
    return false;
  });
  $('#phone').on("copy", function(e) { 
    return false;
  })

  $('#dob').on('keypress', function(e){
    var charCode = (e.which) ? e.which : e.keyCode
    // Accept numbers and slash
    if (charCode > 31 && (charCode < 47 || charCode > 57))
      return false;
    return true; 
  })
  $('#dob').on("paste", function(e) { 
    return false;
  });
  $('#dob').on("copy", function(e) { 
    return false;
  })

  $('.toggle-visibility-1').on('click', function(e) {
    if ($('#password').attr('type') == 'password'){
      $('#password').attr('type', 'text')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\
      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
      </svg>')
    } else {
      $('#password').attr('type', 'password')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\
      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7 7 0 0 0-2.79.588l.77.771A6 6 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755q-.247.248-.517.486z"/>\
      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829"/>\
      <path d="M3.35 5.47q-.27.24-.518.487A13 13 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7 7 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12z"/>\
      </svg>')
    }
  })

  $('.toggle-visibility-2').on('click', function(e) {
    if ($('#confirmation').attr('type') == 'password'){
      $('#confirmation').attr('type', 'text')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\
      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
      </svg>')
    } else {
      $('#confirmation').attr('type', 'password')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\
      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7 7 0 0 0-2.79.588l.77.771A6 6 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755q-.247.248-.517.486z"/>\
      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829"/>\
      <path d="M3.35 5.47q-.27.24-.518.487A13 13 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7 7 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12z"/>\
      </svg>')
    }
  })
}


function account_profile_control(){
  $('#info-form-trigger').on('click', function(){
    $('#info-form').prop('hidden', false)
    $('#account-info').prop('hidden', true)
  })
  $('#email-form-trigger').on('click', function(){
    $('#email-form').prop('hidden', false)
    $('#account-info').prop('hidden', true)
  })
  $('#password-form-trigger').on('click', function(){
    $('#password-form').prop('hidden', false)
    $('#account-info').prop('hidden', true)
  })
  $('#payment-form-trigger').on('click', function(){
    $('#payment-form').prop('hidden', false)
    $('#default-payment').prop('hidden', true)
  })
  $('#cancel-info-form').on('click', function(){
    $('#info-form').prop('hidden', true)
    $('#account-info').prop('hidden', false)
  })
  $('#cancel-email-form').on('click', function(){
    $('#email-form').prop('hidden', true)
    $('#account-info').prop('hidden', false)
  })
  $('#cancel-password-form').on('click', function(){
    $('#password-form').prop('hidden', true)
    $('#account-info').prop('hidden', false)
  })
  $('#cancel-payment-form').on('click', function(){
    $('#payment-form').prop('hidden', true)
    $('#default-payment').prop('hidden', false)
  })

  $('.toggle-visibility-3').on('click', function(e) {
    if ($('#new_password').attr('type') == 'password'){
      $('#new_password').attr('type', 'text')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\
      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
      </svg>')
    } else {
      $('#new_password').attr('type', 'password')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\
      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7 7 0 0 0-2.79.588l.77.771A6 6 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755q-.247.248-.517.486z"/>\
      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829"/>\
      <path d="M3.35 5.47q-.27.24-.518.487A13 13 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7 7 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12z"/>\
      </svg>')
    }
  })
  $('.toggle-visibility-4').on('click', function(e) {
    if ($('#current_password').attr('type') == 'password'){
      $('#current_password').attr('type', 'text')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\
      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
      </svg>')
    } else {
      $('#current_password').attr('type', 'password')
      $(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\
      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7 7 0 0 0-2.79.588l.77.771A6 6 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755q-.247.248-.517.486z"/>\
      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829"/>\
      <path d="M3.35 5.47q-.27.24-.518.487A13 13 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7 7 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12z"/>\
      </svg>')
    }
  })

  $("#default-payment-form").find('form').on( "submit", function( event ) {
    valid_zip = false
    valid_sec = false
    valid_ccn = false
    valid_month = false

    if ($('#zip-code').val().length == 0){
      $('#zip-code-e').text('The Billing ZIP Code field is required.')
      $('#zip-code').addClass('is-invalid')
    } else if ($('#zip-code').val().length != 5){
      $('#zip-code-e').text('The value for the Billing Zip Code field is invalid.')
      $('#zip-code').addClass('is-invalid')
    } else {
      valid_zip = true
    }
    
    if ($('#sec-code').val().length == 0){
      $('#sec-code-e').text('The Card Security Code field is required.')
      $('#sec-code').addClass('is-invalid')
    } else if (!($('#sec-code').val().length >=3 && $('#sec-code').val().length <= 4)){
      $('#sec-code-e').text('The value for the Card Security Code field is invalid.')
      $('#sec-code').addClass('is-invalid')
    } else {
      valid_sec = true
    }

    if (!valid.expirationDate($('#exp-month').val() + '/' + $('#exp-year').val()).isValid){
      $('#exp-month-e').text('The Month field is invalid.')
      $('#exp-month').addClass('is-invalid')
      $('#checkout-button').prop('hidden', true)
    } else {
      valid_month = true
    }

    number = valid.number($('#card-number').val())
    
    if (number.card != null){
      // Validate 
      if (!($('#card-number').val().length >= 8 && $('#card-number').val().length <= 19)){
        $('#card-number-e').text('The Card Number field is not a valid credit card number.')
        $('#card-number').addClass('is-invalid')
      } else {
        if (number.isValid){
          $('#card_type').val(number.card.niceType)
          valid_ccn = true;
        } else {
          $('#card-number-e').text('The Card Number field is not a valid credit card number.')
          $('#card-number').addClass('is-invalid')
        }
      }
    } else {
      if ($('#card-number').val().length == 0){
        $('#card-number-e').text('The Card Number field is required.')
        $('#card-number').addClass('is-invalid')
      } else {
        $('#card-number-e').text('The Card Number field is not a valid credit card number.')
        $('#card-number').addClass('is-invalid')
      }
    }

    if (!(valid_zip && valid_sec && valid_month && valid_ccn)){
      event.preventDefault();
    }
  });
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

      seats_selected = $('#seats_selected').val().split(',')
      seats_selected = seats_selected.filter(e => e != t.data('seat-id'))
      $('#seats_selected').val(seats_selected.toString())

      seats -= 1;
    } else {
      t.addClass('selected')

      if ($('#seats_selected').val() == ''){
        seats_selected = []
      } else {
        seats_selected = $('#seats_selected').val().split(',')
      }
      seats_selected.push(t.data('seat-id'))
      $('#seats_selected').val(seats_selected.toString())

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

},{"card-validator":8}],2:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cardNumber = void 0;
var luhn10 = require("./luhn-10");
var getCardTypes = require("credit-card-type");
function verification(card, isPotentiallyValid, isValid) {
    return {
        card: card,
        isPotentiallyValid: isPotentiallyValid,
        isValid: isValid,
    };
}
function cardNumber(value, options) {
    if (options === void 0) { options = {}; }
    var isPotentiallyValid, isValid, maxLength;
    if (typeof value !== "string" && typeof value !== "number") {
        return verification(null, false, false);
    }
    var testCardValue = String(value).replace(/-|\s/g, "");
    if (!/^\d*$/.test(testCardValue)) {
        return verification(null, false, false);
    }
    var potentialTypes = getCardTypes(testCardValue);
    if (potentialTypes.length === 0) {
        return verification(null, false, false);
    }
    else if (potentialTypes.length !== 1) {
        return verification(null, true, false);
    }
    var cardType = potentialTypes[0];
    if (options.maxLength && testCardValue.length > options.maxLength) {
        return verification(cardType, false, false);
    }
    if (cardType.type === getCardTypes.types.UNIONPAY &&
        options.luhnValidateUnionPay !== true) {
        isValid = true;
    }
    else {
        isValid = luhn10(testCardValue);
    }
    maxLength = Math.max.apply(null, cardType.lengths);
    if (options.maxLength) {
        maxLength = Math.min(options.maxLength, maxLength);
    }
    for (var i = 0; i < cardType.lengths.length; i++) {
        if (cardType.lengths[i] === testCardValue.length) {
            isPotentiallyValid = testCardValue.length < maxLength || isValid;
            return verification(cardType, isPotentiallyValid, isValid);
        }
    }
    return verification(cardType, testCardValue.length < maxLength, false);
}
exports.cardNumber = cardNumber;

},{"./luhn-10":11,"credit-card-type":13}],3:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cardholderName = void 0;
var CARD_NUMBER_REGEX = /^[\d\s-]*$/;
var MAX_LENGTH = 255;
function verification(isValid, isPotentiallyValid) {
    return { isValid: isValid, isPotentiallyValid: isPotentiallyValid };
}
function cardholderName(value) {
    if (typeof value !== "string") {
        return verification(false, false);
    }
    if (value.length === 0) {
        return verification(false, true);
    }
    if (value.length > MAX_LENGTH) {
        return verification(false, false);
    }
    if (CARD_NUMBER_REGEX.test(value)) {
        return verification(false, true);
    }
    return verification(true, true);
}
exports.cardholderName = cardholderName;

},{}],4:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cvv = void 0;
var DEFAULT_LENGTH = 3;
function includes(array, thing) {
    for (var i = 0; i < array.length; i++) {
        if (thing === array[i]) {
            return true;
        }
    }
    return false;
}
function max(array) {
    var maximum = DEFAULT_LENGTH;
    var i = 0;
    for (; i < array.length; i++) {
        maximum = array[i] > maximum ? array[i] : maximum;
    }
    return maximum;
}
function verification(isValid, isPotentiallyValid) {
    return { isValid: isValid, isPotentiallyValid: isPotentiallyValid };
}
function cvv(value, maxLength) {
    if (maxLength === void 0) { maxLength = DEFAULT_LENGTH; }
    maxLength = maxLength instanceof Array ? maxLength : [maxLength];
    if (typeof value !== "string") {
        return verification(false, false);
    }
    if (!/^\d*$/.test(value)) {
        return verification(false, false);
    }
    if (includes(maxLength, value.length)) {
        return verification(true, true);
    }
    if (value.length < Math.min.apply(null, maxLength)) {
        return verification(false, true);
    }
    if (value.length > max(maxLength)) {
        return verification(false, false);
    }
    return verification(true, true);
}
exports.cvv = cvv;

},{}],5:[function(require,module,exports){
"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.expirationDate = void 0;
var parse_date_1 = require("./lib/parse-date");
var expiration_month_1 = require("./expiration-month");
var expiration_year_1 = require("./expiration-year");
function verification(isValid, isPotentiallyValid, month, year) {
    return {
        isValid: isValid,
        isPotentiallyValid: isPotentiallyValid,
        month: month,
        year: year,
    };
}
function expirationDate(value, maxElapsedYear) {
    var date;
    if (typeof value === "string") {
        value = value.replace(/^(\d\d) (\d\d(\d\d)?)$/, "$1/$2");
        date = (0, parse_date_1.parseDate)(String(value));
    }
    else if (value !== null && typeof value === "object") {
        var fullDate = __assign({}, value);
        date = {
            month: String(fullDate.month),
            year: String(fullDate.year),
        };
    }
    else {
        return verification(false, false, null, null);
    }
    var monthValid = (0, expiration_month_1.expirationMonth)(date.month);
    var yearValid = (0, expiration_year_1.expirationYear)(date.year, maxElapsedYear);
    if (monthValid.isValid) {
        if (yearValid.isCurrentYear) {
            var isValidForThisYear = monthValid.isValidForThisYear;
            return verification(isValidForThisYear, isValidForThisYear, date.month, date.year);
        }
        if (yearValid.isValid) {
            return verification(true, true, date.month, date.year);
        }
    }
    if (monthValid.isPotentiallyValid && yearValid.isPotentiallyValid) {
        return verification(false, true, null, null);
    }
    return verification(false, false, null, null);
}
exports.expirationDate = expirationDate;

},{"./expiration-month":6,"./expiration-year":7,"./lib/parse-date":10}],6:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.expirationMonth = void 0;
function verification(isValid, isPotentiallyValid, isValidForThisYear) {
    return {
        isValid: isValid,
        isPotentiallyValid: isPotentiallyValid,
        isValidForThisYear: isValidForThisYear || false,
    };
}
function expirationMonth(value) {
    var currentMonth = new Date().getMonth() + 1;
    if (typeof value !== "string") {
        return verification(false, false);
    }
    if (value.replace(/\s/g, "") === "" || value === "0") {
        return verification(false, true);
    }
    if (!/^\d*$/.test(value)) {
        return verification(false, false);
    }
    var month = parseInt(value, 10);
    if (isNaN(Number(value))) {
        return verification(false, false);
    }
    var result = month > 0 && month < 13;
    return verification(result, result, result && month >= currentMonth);
}
exports.expirationMonth = expirationMonth;

},{}],7:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.expirationYear = void 0;
var DEFAULT_VALID_NUMBER_OF_YEARS_IN_THE_FUTURE = 19;
function verification(isValid, isPotentiallyValid, isCurrentYear) {
    return {
        isValid: isValid,
        isPotentiallyValid: isPotentiallyValid,
        isCurrentYear: isCurrentYear || false,
    };
}
function expirationYear(value, maxElapsedYear) {
    if (maxElapsedYear === void 0) { maxElapsedYear = DEFAULT_VALID_NUMBER_OF_YEARS_IN_THE_FUTURE; }
    var isCurrentYear;
    if (typeof value !== "string") {
        return verification(false, false);
    }
    if (value.replace(/\s/g, "") === "") {
        return verification(false, true);
    }
    if (!/^\d*$/.test(value)) {
        return verification(false, false);
    }
    var len = value.length;
    if (len < 2) {
        return verification(false, true);
    }
    var currentYear = new Date().getFullYear();
    if (len === 3) {
        // 20x === 20x
        var firstTwo = value.slice(0, 2);
        var currentFirstTwo = String(currentYear).slice(0, 2);
        return verification(false, firstTwo === currentFirstTwo);
    }
    if (len > 4) {
        return verification(false, false);
    }
    var numericValue = parseInt(value, 10);
    var twoDigitYear = Number(String(currentYear).substr(2, 2));
    var valid = false;
    if (len === 2) {
        if (String(currentYear).substr(0, 2) === value) {
            return verification(false, true);
        }
        isCurrentYear = twoDigitYear === numericValue;
        valid =
            numericValue >= twoDigitYear &&
                numericValue <= twoDigitYear + maxElapsedYear;
    }
    else if (len === 4) {
        isCurrentYear = currentYear === numericValue;
        valid =
            numericValue >= currentYear &&
                numericValue <= currentYear + maxElapsedYear;
    }
    return verification(valid, valid, isCurrentYear);
}
exports.expirationYear = expirationYear;

},{}],8:[function(require,module,exports){
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var creditCardType = __importStar(require("credit-card-type"));
var cardholder_name_1 = require("./cardholder-name");
var card_number_1 = require("./card-number");
var expiration_date_1 = require("./expiration-date");
var expiration_month_1 = require("./expiration-month");
var expiration_year_1 = require("./expiration-year");
var cvv_1 = require("./cvv");
var postal_code_1 = require("./postal-code");
var cardValidator = {
    creditCardType: creditCardType,
    cardholderName: cardholder_name_1.cardholderName,
    number: card_number_1.cardNumber,
    expirationDate: expiration_date_1.expirationDate,
    expirationMonth: expiration_month_1.expirationMonth,
    expirationYear: expiration_year_1.expirationYear,
    cvv: cvv_1.cvv,
    postalCode: postal_code_1.postalCode,
};
module.exports = cardValidator;

},{"./card-number":2,"./cardholder-name":3,"./cvv":4,"./expiration-date":5,"./expiration-month":6,"./expiration-year":7,"./postal-code":12,"credit-card-type":13}],9:[function(require,module,exports){
"use strict";
// Polyfill taken from <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/isArray#Polyfill>.
Object.defineProperty(exports, "__esModule", { value: true });
exports.isArray = void 0;
exports.isArray = Array.isArray ||
    function (arg) {
        return Object.prototype.toString.call(arg) === "[object Array]";
    };

},{}],10:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseDate = void 0;
var expiration_year_1 = require("../expiration-year");
var is_array_1 = require("./is-array");
function getNumberOfMonthDigitsInDateString(dateString) {
    var firstCharacter = Number(dateString[0]);
    var assumedYear;
    /*
      if the first character in the string starts with `0`,
      we know that the month will be 2 digits.
  
      '0122' => {month: '01', year: '22'}
    */
    if (firstCharacter === 0) {
        return 2;
    }
    /*
      if the first character in the string starts with
      number greater than 1, it must be a 1 digit month
  
      '322' => {month: '3', year: '22'}
    */
    if (firstCharacter > 1) {
        return 1;
    }
    /*
      if the first 2 characters make up a number between
      13-19, we know that the month portion must be 1
  
      '139' => {month: '1', year: '39'}
    */
    if (firstCharacter === 1 && Number(dateString[1]) > 2) {
        return 1;
    }
    /*
      if the first 2 characters make up a number between
      10-12, we check if the year portion would be considered
      valid if we assumed that the month was 1. If it is
      not potentially valid, we assume the month must have
      2 digits.
  
      '109' => {month: '10', year: '9'}
      '120' => {month: '1', year: '20'} // when checked in the year 2019
      '120' => {month: '12', year: '0'} // when checked in the year 2021
    */
    if (firstCharacter === 1) {
        assumedYear = dateString.substr(1);
        return (0, expiration_year_1.expirationYear)(assumedYear).isPotentiallyValid ? 1 : 2;
    }
    /*
      If the length of the value is exactly 5 characters,
      we assume a full year was passed in, meaning the remaining
      single leading digit must be the month value.
  
      '12202' => {month: '1', year: '2202'}
    */
    if (dateString.length === 5) {
        return 1;
    }
    /*
      If the length of the value is more than five characters,
      we assume a full year was passed in addition to the month
      and therefore the month portion must be 2 digits.
  
      '112020' => {month: '11', year: '2020'}
    */
    if (dateString.length > 5) {
        return 2;
    }
    /*
      By default, the month value is the first value
    */
    return 1;
}
function parseDate(datestring) {
    var date;
    if (/^\d{4}-\d{1,2}$/.test(datestring)) {
        date = datestring.split("-").reverse();
    }
    else if (/\//.test(datestring)) {
        date = datestring.split(/\s*\/\s*/g);
    }
    else if (/\s/.test(datestring)) {
        date = datestring.split(/ +/g);
    }
    if ((0, is_array_1.isArray)(date)) {
        return {
            month: date[0] || "",
            year: date.slice(1).join(),
        };
    }
    var numberOfDigitsInMonth = getNumberOfMonthDigitsInDateString(datestring);
    var month = datestring.substr(0, numberOfDigitsInMonth);
    return {
        month: month,
        year: datestring.substr(month.length),
    };
}
exports.parseDate = parseDate;

},{"../expiration-year":7,"./is-array":9}],11:[function(require,module,exports){
/* eslint-disable */
/*
 * Luhn algorithm implementation in JavaScript
 * Copyright (c) 2009 Nicholas C. Zakas
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
"use strict";
function luhn10(identifier) {
    var sum = 0;
    var alt = false;
    var i = identifier.length - 1;
    var num;
    while (i >= 0) {
        num = parseInt(identifier.charAt(i), 10);
        if (alt) {
            num *= 2;
            if (num > 9) {
                num = (num % 10) + 1; // eslint-disable-line no-extra-parens
            }
        }
        alt = !alt;
        sum += num;
        i--;
    }
    return sum % 10 === 0;
}
module.exports = luhn10;

},{}],12:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.postalCode = void 0;
var DEFAULT_MIN_POSTAL_CODE_LENGTH = 3;
function verification(isValid, isPotentiallyValid) {
    return { isValid: isValid, isPotentiallyValid: isPotentiallyValid };
}
function postalCode(value, options) {
    if (options === void 0) { options = {}; }
    var minLength = options.minLength || DEFAULT_MIN_POSTAL_CODE_LENGTH;
    if (typeof value !== "string") {
        return verification(false, false);
    }
    else if (value.length < minLength) {
        return verification(false, true);
    }
    return verification(true, true);
}
exports.postalCode = postalCode;

},{}],13:[function(require,module,exports){
"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var cardTypes = require("./lib/card-types");
var add_matching_cards_to_results_1 = require("./lib/add-matching-cards-to-results");
var is_valid_input_type_1 = require("./lib/is-valid-input-type");
var find_best_match_1 = require("./lib/find-best-match");
var clone_1 = require("./lib/clone");
var customCards = {};
var cardNames = {
    VISA: "visa",
    MASTERCARD: "mastercard",
    AMERICAN_EXPRESS: "american-express",
    DINERS_CLUB: "diners-club",
    DISCOVER: "discover",
    JCB: "jcb",
    UNIONPAY: "unionpay",
    MAESTRO: "maestro",
    ELO: "elo",
    MIR: "mir",
    HIPER: "hiper",
    HIPERCARD: "hipercard",
};
var ORIGINAL_TEST_ORDER = [
    cardNames.VISA,
    cardNames.MASTERCARD,
    cardNames.AMERICAN_EXPRESS,
    cardNames.DINERS_CLUB,
    cardNames.DISCOVER,
    cardNames.JCB,
    cardNames.UNIONPAY,
    cardNames.MAESTRO,
    cardNames.ELO,
    cardNames.MIR,
    cardNames.HIPER,
    cardNames.HIPERCARD,
];
var testOrder = clone_1.clone(ORIGINAL_TEST_ORDER);
function findType(cardType) {
    return customCards[cardType] || cardTypes[cardType];
}
function getAllCardTypes() {
    return testOrder.map(function (cardType) { return clone_1.clone(findType(cardType)); });
}
function getCardPosition(name, ignoreErrorForNotExisting) {
    if (ignoreErrorForNotExisting === void 0) { ignoreErrorForNotExisting = false; }
    var position = testOrder.indexOf(name);
    if (!ignoreErrorForNotExisting && position === -1) {
        throw new Error('"' + name + '" is not a supported card type.');
    }
    return position;
}
function creditCardType(cardNumber) {
    var results = [];
    if (!is_valid_input_type_1.isValidInputType(cardNumber)) {
        return results;
    }
    if (cardNumber.length === 0) {
        return getAllCardTypes();
    }
    testOrder.forEach(function (cardType) {
        var cardConfiguration = findType(cardType);
        add_matching_cards_to_results_1.addMatchingCardsToResults(cardNumber, cardConfiguration, results);
    });
    var bestMatch = find_best_match_1.findBestMatch(results);
    if (bestMatch) {
        return [bestMatch];
    }
    return results;
}
creditCardType.getTypeInfo = function (cardType) {
    return clone_1.clone(findType(cardType));
};
creditCardType.removeCard = function (name) {
    var position = getCardPosition(name);
    testOrder.splice(position, 1);
};
creditCardType.addCard = function (config) {
    var existingCardPosition = getCardPosition(config.type, true);
    customCards[config.type] = config;
    if (existingCardPosition === -1) {
        testOrder.push(config.type);
    }
};
creditCardType.updateCard = function (cardType, updates) {
    var originalObject = customCards[cardType] || cardTypes[cardType];
    if (!originalObject) {
        throw new Error("\"" + cardType + "\" is not a recognized type. Use `addCard` instead.'");
    }
    if (updates.type && originalObject.type !== updates.type) {
        throw new Error("Cannot overwrite type parameter.");
    }
    var clonedCard = clone_1.clone(originalObject);
    clonedCard = __assign(__assign({}, clonedCard), updates);
    customCards[clonedCard.type] = clonedCard;
};
creditCardType.changeOrder = function (name, position) {
    var currentPosition = getCardPosition(name);
    testOrder.splice(currentPosition, 1);
    testOrder.splice(position, 0, name);
};
creditCardType.resetModifications = function () {
    testOrder = clone_1.clone(ORIGINAL_TEST_ORDER);
    customCards = {};
};
creditCardType.types = cardNames;
module.exports = creditCardType;

},{"./lib/add-matching-cards-to-results":14,"./lib/card-types":15,"./lib/clone":16,"./lib/find-best-match":17,"./lib/is-valid-input-type":18}],14:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.addMatchingCardsToResults = void 0;
var clone_1 = require("./clone");
var matches_1 = require("./matches");
function addMatchingCardsToResults(cardNumber, cardConfiguration, results) {
    var i, patternLength;
    for (i = 0; i < cardConfiguration.patterns.length; i++) {
        var pattern = cardConfiguration.patterns[i];
        if (!matches_1.matches(cardNumber, pattern)) {
            continue;
        }
        var clonedCardConfiguration = clone_1.clone(cardConfiguration);
        if (Array.isArray(pattern)) {
            patternLength = String(pattern[0]).length;
        }
        else {
            patternLength = String(pattern).length;
        }
        if (cardNumber.length >= patternLength) {
            clonedCardConfiguration.matchStrength = patternLength;
        }
        results.push(clonedCardConfiguration);
        break;
    }
}
exports.addMatchingCardsToResults = addMatchingCardsToResults;

},{"./clone":16,"./matches":19}],15:[function(require,module,exports){
"use strict";
var cardTypes = {
    visa: {
        niceType: "Visa",
        type: "visa",
        patterns: [4],
        gaps: [4, 8, 12],
        lengths: [16, 18, 19],
        code: {
            name: "CVV",
            size: 3,
        },
    },
    mastercard: {
        niceType: "Mastercard",
        type: "mastercard",
        patterns: [[51, 55], [2221, 2229], [223, 229], [23, 26], [270, 271], 2720],
        gaps: [4, 8, 12],
        lengths: [16],
        code: {
            name: "CVC",
            size: 3,
        },
    },
    "american-express": {
        niceType: "American Express",
        type: "american-express",
        patterns: [34, 37],
        gaps: [4, 10],
        lengths: [15],
        code: {
            name: "CID",
            size: 4,
        },
    },
    "diners-club": {
        niceType: "Diners Club",
        type: "diners-club",
        patterns: [[300, 305], 36, 38, 39],
        gaps: [4, 10],
        lengths: [14, 16, 19],
        code: {
            name: "CVV",
            size: 3,
        },
    },
    discover: {
        niceType: "Discover",
        type: "discover",
        patterns: [6011, [644, 649], 65],
        gaps: [4, 8, 12],
        lengths: [16, 19],
        code: {
            name: "CID",
            size: 3,
        },
    },
    jcb: {
        niceType: "JCB",
        type: "jcb",
        patterns: [2131, 1800, [3528, 3589]],
        gaps: [4, 8, 12],
        lengths: [16, 17, 18, 19],
        code: {
            name: "CVV",
            size: 3,
        },
    },
    unionpay: {
        niceType: "UnionPay",
        type: "unionpay",
        patterns: [
            620,
            [624, 626],
            [62100, 62182],
            [62184, 62187],
            [62185, 62197],
            [62200, 62205],
            [622010, 622999],
            622018,
            [622019, 622999],
            [62207, 62209],
            [622126, 622925],
            [623, 626],
            6270,
            6272,
            6276,
            [627700, 627779],
            [627781, 627799],
            [6282, 6289],
            6291,
            6292,
            810,
            [8110, 8131],
            [8132, 8151],
            [8152, 8163],
            [8164, 8171],
        ],
        gaps: [4, 8, 12],
        lengths: [14, 15, 16, 17, 18, 19],
        code: {
            name: "CVN",
            size: 3,
        },
    },
    maestro: {
        niceType: "Maestro",
        type: "maestro",
        patterns: [
            493698,
            [500000, 504174],
            [504176, 506698],
            [506779, 508999],
            [56, 59],
            63,
            67,
            6,
        ],
        gaps: [4, 8, 12],
        lengths: [12, 13, 14, 15, 16, 17, 18, 19],
        code: {
            name: "CVC",
            size: 3,
        },
    },
    elo: {
        niceType: "Elo",
        type: "elo",
        patterns: [
            401178,
            401179,
            438935,
            457631,
            457632,
            431274,
            451416,
            457393,
            504175,
            [506699, 506778],
            [509000, 509999],
            627780,
            636297,
            636368,
            [650031, 650033],
            [650035, 650051],
            [650405, 650439],
            [650485, 650538],
            [650541, 650598],
            [650700, 650718],
            [650720, 650727],
            [650901, 650978],
            [651652, 651679],
            [655000, 655019],
            [655021, 655058],
        ],
        gaps: [4, 8, 12],
        lengths: [16],
        code: {
            name: "CVE",
            size: 3,
        },
    },
    mir: {
        niceType: "Mir",
        type: "mir",
        patterns: [[2200, 2204]],
        gaps: [4, 8, 12],
        lengths: [16, 17, 18, 19],
        code: {
            name: "CVP2",
            size: 3,
        },
    },
    hiper: {
        niceType: "Hiper",
        type: "hiper",
        patterns: [637095, 63737423, 63743358, 637568, 637599, 637609, 637612],
        gaps: [4, 8, 12],
        lengths: [16],
        code: {
            name: "CVC",
            size: 3,
        },
    },
    hipercard: {
        niceType: "Hipercard",
        type: "hipercard",
        patterns: [606282],
        gaps: [4, 8, 12],
        lengths: [16],
        code: {
            name: "CVC",
            size: 3,
        },
    },
};
module.exports = cardTypes;

},{}],16:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.clone = void 0;
function clone(originalObject) {
    if (!originalObject) {
        return null;
    }
    return JSON.parse(JSON.stringify(originalObject));
}
exports.clone = clone;

},{}],17:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.findBestMatch = void 0;
function hasEnoughResultsToDetermineBestMatch(results) {
    var numberOfResultsWithMaxStrengthProperty = results.filter(function (result) { return result.matchStrength; }).length;
    /*
     * if all possible results have a maxStrength property that means the card
     * number is sufficiently long enough to determine conclusively what the card
     * type is
     * */
    return (numberOfResultsWithMaxStrengthProperty > 0 &&
        numberOfResultsWithMaxStrengthProperty === results.length);
}
function findBestMatch(results) {
    if (!hasEnoughResultsToDetermineBestMatch(results)) {
        return null;
    }
    return results.reduce(function (bestMatch, result) {
        if (!bestMatch) {
            return result;
        }
        /*
         * If the current best match pattern is less specific than this result, set
         * the result as the new best match
         * */
        if (Number(bestMatch.matchStrength) < Number(result.matchStrength)) {
            return result;
        }
        return bestMatch;
    });
}
exports.findBestMatch = findBestMatch;

},{}],18:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.isValidInputType = void 0;
function isValidInputType(cardNumber) {
    return typeof cardNumber === "string" || cardNumber instanceof String;
}
exports.isValidInputType = isValidInputType;

},{}],19:[function(require,module,exports){
"use strict";
/*
 * Adapted from https://github.com/polvo-labs/card-type/blob/aaab11f80fa1939bccc8f24905a06ae3cd864356/src/cardType.js#L37-L42
 * */
Object.defineProperty(exports, "__esModule", { value: true });
exports.matches = void 0;
function matchesRange(cardNumber, min, max) {
    var maxLengthToCheck = String(min).length;
    var substr = cardNumber.substr(0, maxLengthToCheck);
    var integerRepresentationOfCardNumber = parseInt(substr, 10);
    min = parseInt(String(min).substr(0, substr.length), 10);
    max = parseInt(String(max).substr(0, substr.length), 10);
    return (integerRepresentationOfCardNumber >= min &&
        integerRepresentationOfCardNumber <= max);
}
function matchesPattern(cardNumber, pattern) {
    pattern = String(pattern);
    return (pattern.substring(0, cardNumber.length) ===
        cardNumber.substring(0, pattern.length));
}
function matches(cardNumber, pattern) {
    if (Array.isArray(pattern)) {
        return matchesRange(cardNumber, pattern[0], pattern[1]);
    }
    return matchesPattern(cardNumber, pattern);
}
exports.matches = matches;

},{}]},{},[1]);
