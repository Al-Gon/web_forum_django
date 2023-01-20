$(document).ready(function() {
    ymaps.ready(init);
    function init () {
        let map = new ymaps.Map("YMapsID", {
            center: [55.751574, 37.573856],
            zoom: 7,
            controls: ['routePanelControl']
        });
        // Создаем геообъект с типом геометрии "Точка".
        myPlacemark = new ymaps.Placemark([56.577313, 36.708036], {
            iconContent: 'СНТ "Мечта2"'
        }, {
        // Красная иконка, растягивающаяся под содержимое.
        preset: "islands#redStretchyIcon"
        });
        map.geoObjects.add(myPlacemark);

        let trafficControl = new ymaps.control.TrafficControl({ state: {
            // Отображаются пробки "Сейчас".
            providerKey: 'traffic#actual',
            // Начинаем сразу показывать пробки на карте.
            trafficShown: false
        }});
        // Добавим контрол на карту.
        map.controls.add(trafficControl);
        // Получим ссылку на провайдер пробок "Сейчас" и включим показ инфоточек.
        trafficControl.getProvider('traffic#actual').state.set('infoLayerShown', true);

        // geolocation.get({
        //     provider: 'browser',
        //     mapStateAutoApply: true
        // }).then(function (result) {
        //     // Синим цветом пометим положение, полученное через браузер.
        //     // Если браузер не поддерживает эту функциональность, метка не будет добавлена на карту.
        //     result.geoObjects.options.set('preset', 'islands#blueCircleIcon');
        //     map.geoObjects.add(result.geoObjects);
        // });


        let control = map.controls.get('routePanelControl');

        // Зададим состояние панели для построения машрутов.
        control.routePanel.state.set({
            // Тип маршрутизации.
            type: 'masstransit',
            // Выключим возможность задавать пункт отправления в поле ввода.
            fromEnabled: true,
            // Адрес или координаты пункта отправления.
            //from: 'Москва, Льва Толстого 16',
            // Включим возможность задавать пункт назначения в поле ввода.
            toEnabled: false,
            // Адрес или координаты пункта назначения.
            to: [56.577313, 36.708036]
        });

        // Зададим опции панели для построения машрутов.
        control.routePanel.options.set({
            // Запрещаем показ кнопки, позволяющей менять местами начальную и конечную точки маршрута.
            allowSwitch: false,
            // Включим определение адреса по координатам клика.
            // Адрес будет автоматически подставляться в поле ввода на панели, а также в подпись метки маршрута.
            reverseGeocoding: true,
            // Зададим виды маршрутизации, которые будут доступны пользователям для выбора.
            types: { masstransit: true, pedestrian: true, taxi: true }
        });

        // // Создаем кнопку, с помощью которой пользователи смогут менять местами начальную и конечную точки маршрута.
        // let switchPointsButton = new ymaps.control.Button({
        //     data: {content: "Поменять местами", title: "Поменять точки местами"},
        //     options: {selectOnClick: false, maxWidth: 160}
        // });
        // // Объявляем обработчик для кнопки.
        // switchPointsButton.events.add('click', function () {
        //     // Меняет местами начальную и конечную точки маршрута.
        //     control.routePanel.switchPoints();
        // });
        // map.controls.add(switchPointsButton);
    };

    //функция для перехода на страницу с картой и скролинга
    // function showMap(){
	// 	UIkit.scroll('#YMapsID',{offset: 60}).scrollTo('#YMapsID');
	// 	window.removeEventListener("load",showMap);
	// };
	//
	// if(location.search == "?show_map=1"){
	//     window.addEventListener("load",showMap);
	// };

    function fadeout_raw(json) {
        if (json) {
            let topic_id = json.topic_id;
            let row = $('div[data-row-id=' + topic_id + ']');
            row.delay(1000).fadeOut(100,
                function () {
                    $(this).remove();
                    if (!$(".check-input").length) {
                        window.location = location.href;
                    }
                });
        }
    }

    function set_message(elem) {
        let topic_id = elem.attr("data-id");
        let checked = elem.prop("checked");
        $.ajax({
            type: 'POST',
            url: elem.attr("action"),
            data: {"topic_id": topic_id,
                  "checked": checked
                  },
            dataType: "json",

            success: function (json) {
                console.log(json); // log the returned json to the console
                console.log("success"); // another sanity check
                fadeout_raw(json);

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

