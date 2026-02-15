jQuery(function($) {
    let carouselWrap = $('.carousel');
    let loaderWrap = $('#loader');
    let endLoaderWrap = $('#end-loader');
    let contactDataWrap = $('#contact-data') ;
    let leadForm = $('#leadForm');


    $('.showNext').click(function() {
        let stepWrap = $(this).closest('.step');
        let step = stepWrap.attr('data-step');
        let nextstep = parseInt(step) + 1;
        let nextstepWrap = $('.step' + nextstep);

        let answer_selected = $(this).attr('data-val');
        $(stepWrap).find('.answer').val(answer_selected);

        if($(nextstepWrap).length) {
            $(stepWrap).hide();
            $(stepWrap).removeClass('active');
            $(carouselWrap).find('.step' + nextstep).show();
        }

        update_stepper(parseInt(step));

    });

    $('.showLoader').click(function() {
        let answer_selected = $(this).attr('data-val');
        $(this).closest('.step').find('.answer').val(answer_selected);
        $('.step').hide();
        $(loaderWrap).show();

        setTimeout(function(){
            $(loaderWrap).hide();
            $(endLoaderWrap).show();

            setTimeout(function(){
                $(endLoaderWrap).hide();
                $(contactDataWrap).show();
            }, 1500);
        }, 1500);
    });

    $(leadForm).submit(function (){
        $(contactDataWrap).hide();
        $(loaderWrap).show();
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
