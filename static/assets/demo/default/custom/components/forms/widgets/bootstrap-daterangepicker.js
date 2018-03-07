var BootstrapDaterangepicker = function () {
    // var today = new Date();
    // var dd = today.getDate();
    // var mm = today.getMonth()+1; //January is 0!
    // var mmmax = today.getMonth()+2;
    // var yyyy = today.getFullYear();
    // if(dd<10){ dd='0'+dd }
    // if(mm<10){ mm='0'+mm }
    // var tday = mm+'/'+dd+'/'+yyyy;
    // var maxDate = mmmax+'/01/'+yyyy;
    // var currentTime = new Date()
    var currentTime = new Date();
    var minDate = new Date(currentTime.getFullYear(), currentTime.getMonth(), +1); //one day next before month
    var maxDate =  new Date(currentTime.getFullYear(), currentTime.getMonth() +1, -1); // one day before next month

    var a = function () {
        $("#m_daterangepicker_1").daterangepicker({
            buttonClasses: "m-btn btn",
            applyClass: "btn-primary",
            cancelClass: "btn-secondary"
        });

    };
    return {
        init: function () {
            a()
        }
    }
}();
jQuery(document).ready(function () {
    BootstrapDaterangepicker.init()
});