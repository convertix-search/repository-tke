jQuery(function($) {
    let carouselWrap = $('.carousel');
    let loaderWrap = $('#loader');
    let contactDataWrap = $('#contact-data') ;
    let leadForm = $('#leadForm');


    $('.showNext').click(function() {
        let stepWrap = $(this).closest('.step');
        let step = stepWrap.attr('data-step');
        let nextstep = parseInt(step) + 1;

        let answer_selected = $(this).attr('data-val');
        $(stepWrap).find('.answer').val(answer_selected);

        $(stepWrap).hide();
        $(stepWrap).removeClass('active');
        $(carouselWrap).find('.step' + nextstep).show();

        update_stepper(parseInt(step));
    });

    // Only allow digits and + at the start in the phone field
    $('#input_phone').on('keydown', function(e) {
        var allowedKeys = ['Backspace','Delete','Tab','Escape','Enter','ArrowLeft','ArrowRight','Home','End'];
        if (allowedKeys.indexOf(e.key) !== -1) return;
        if (e.key === '+' && this.selectionStart === 0 && this.value.indexOf('+') === -1) return;
        if (!/^\d$/.test(e.key)) {
            e.preventDefault();
        }
    });
    // Strip non-numeric characters if pasted in
    $('#input_phone').on('input', function() {
        var val = this.value;
        var hasPlus = val.startsWith('+');
        var digits = val.replace(/\D/g, '');
        this.value = (hasPlus ? '+' : '') + digits;
    });

    $(leadForm).submit(function(e) {
        // Always prevent default — we control submission explicitly
        e.preventDefault();

        var phoneInput = $('#input_phone');
        var emailInput = $('#input_email');
        var phoneError = $('#phone-error');
        var emailError = $('#email-error');
        var valid = true;

        // Phone validation: optional leading + then 10-15 digits
        var phoneVal = phoneInput.val().replace(/\s+/g, '');
        var phonePattern = /^\+?\d{10,15}$/;
        if (!phonePattern.test(phoneVal)) {
            phoneError.show();
            phoneInput.addClass('is-invalid');
            valid = false;
        } else {
            phoneError.hide();
            phoneInput.removeClass('is-invalid');
        }

        // Email validation: simple regex check (novalidate disables browser check)
        var emailVal = emailInput.val().trim();
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailVal)) {
            emailError.show();
            emailInput.addClass('is-invalid');
            valid = false;
        } else {
            emailError.hide();
            emailInput.removeClass('is-invalid');
        }

        if (!valid) {
            return;
        }

        // All valid: show loader, hide contact form, then submit natively
        $(contactDataWrap).hide();
        $(loaderWrap).show();
        leadForm[0].submit();
    });

    function update_stepper(step){
        var items = $('.stepper-item');
        $(items).removeClass('completed active');
        $(items).each(function( index, element ) {
            if(index < step){
                $(element).addClass('completed');
            }else if(index === step){
                $(element).addClass('active');
            }
        });
    }

});

