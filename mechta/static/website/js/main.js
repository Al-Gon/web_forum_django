$(document).ready(function() {
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
            },
            error: function (xhr,  errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        })
    };

    $(document).on("change", ".message_box", function(){
        set_message($(this));
    });


    $(document).on("click", "a.mark-all-messages", function (event) {
		if ($(this).attr("href") == '#'){
			event.preventDefault();
		};
        $(".message_box").each(function() {
            if ($(this).prop("checked") == false){
                $(this).prop("checked", true);
                set_message($(this));
            }
        })
    });






});

