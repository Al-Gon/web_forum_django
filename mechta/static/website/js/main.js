$(document).ready(function() {

    function fadeout_raw(elem) {
        let row = elem.parent().parent();
        if (row.attr('data-raw-id') == elem.attr('data-id')) {
            row.delay(1000).fadeOut(100,
                function (el=row) {
                    el.remove();
                    if (!$(".check-input").length) {
                       window.location = location.href;
                    }
                });
        }
    }

    function set_message(elem) {
        let pk = elem.attr("data-id");
        let checked = elem.prop("checked");
        $.ajax({
            type: 'POST',
            url: elem.attr("action"),
            data: {"pk": pk,
                  "checked": checked
                  },
            dataType: "json",

            success: function (json) {
                console.log(json); // log the returned json to the console
                console.log("success"); // another sanity check
                fadeout_raw(elem);

            },
            error: function (xhr,  errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        })
    }

    $(document).on("change", ".message_box", function(){
            if($(this).prop("checked")) {
                set_message($(this));
            }
    });


    $(document).on("click", "a.mark-all-topics", function (event) {
		if ($(this).attr("href") == '#'){
			event.preventDefault();
		}
        $(".message_box").each(function() {
            if (!$(this).prop("checked")){
                $(this).prop("checked", true);
                set_message($(this));
            }
        })
    });
});

