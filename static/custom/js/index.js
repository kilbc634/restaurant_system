var myTable_val = 0;
var myMoney_val = 0;

function btn_plus_value(num) {
    var cards = document.getElementsByClassName("card-wrapper");
    var card = cards[num];
    var value_btn = card.getElementsByTagName("a")[1];
    var number = parseInt(value_btn.innerText);
    number += 1;
    value_btn.innerText = number.toString();

    var cost_str = card.getElementsByTagName("p")[0].innerText;
    var cost_val = parseInt(cost_str.split(" ")[1]);
    myMoney_val += cost_val;
    moneyView_updata()
}

function btn_minus_value(num) {
    var cards = document.getElementsByClassName("card-wrapper");
    var card = cards[num];

    var value_btn = card.getElementsByTagName("a")[1];
    var number = parseInt(value_btn.innerText);
    if(number > 0){
        number -= 1;
        value_btn.innerText = number.toString();

        var cost_str = card.getElementsByTagName("p")[0].innerText;
        var cost_val = parseInt(cost_str.split(" ")[1]);
        myMoney_val -= cost_val;
        moneyView_updata()
    } 
}

function moneyView_updata() {
    var title_money_obj = document.getElementsByClassName("navbar-caption-wrap")[0].getElementsByTagName("a")[0];
    title_money_obj.innerText = "總金額 NT$ " + myMoney_val;
}

function setTable() {
    var input_str = prompt("請輸入桌號", myTable_val.toString());
    var value = parseInt(input_str);
    if(value){
        myTable_val = value;
    }
    else{
        if(myTable_val == 0) {
            alert("桌號設定錯誤，請重新設定");
        }
    }
}

$(function () {
    var div_title_btn = document.getElementsByClassName("navbar-buttons mbr-section-btn")[0];
    var title_btn_objs = div_title_btn.getElementsByTagName("a");
    var title_setTable_obj = title_btn_objs[0];
    var title_viewBackLog_obj = title_btn_objs[1];
    title_setTable_obj.onclick = Function("setTable()");

    var VmenuSection = new Vue({
        el: '#menuZone',
        delimiters: ['${', '}'],
        data: {
            backgrounds: [
                'cid-rrLCDGt7He',
                'cid-rrQ3YsmoMI',
                'cid-rrQ3ZpScas'
            ],
            menuDatas: []
            // menuDatas_sample: [
            //     {
            //         'background': 'cid-rrQ3YsmoMI',
            //         'menu': [
            //             {
            //                 'name': '豬排＋雞腿排',
            //                 'cost': '270',
            //                 'image': 'static/assets/images/large-d1ce75da8130b4f8-1-492x369.jpg'
            //             },
            //             {
            //                 'name': '豬排＋雞腿排',
            //                 'cost': '270',
            //                 'image': 'static/assets/images/large-d1ce75da8130b4f8-1-492x369.jpg'
            //             },
            //             ...
            //         ]
            //     },
            //     ...
            // ]
        },
        methods: {
            updateMenuView: function (menuList) {
                for (let index = 0; index < menuList.length; index++) {
                    if (index % 4 === 0) {
                        this.menuDatas.push({
                            'background': this.backgrounds[(index / 4) % this.backgrounds.length],
                            'menu': []
                        });
                    }
                    var menu = {
                        'name': menuList[index]['menu'],
                        'cost': menuList[index]['cost'],
                        'image': menuList[index]['img']
                    }
                    this.menuDatas[this.menuDatas.length - 1]['menu'].push(menu);
                }
            }
        }
    })

    function addClickEvent_forAllCounterBtn() {
        var cards = document.getElementsByClassName("card-wrapper");
        for(var i = 0; i < cards.length; i++){
            var card = cards[i];
            var plus_btn = card.getElementsByTagName("a")[0];
            plus_btn.onclick = Function(`btn_plus_value(${i})`)
            var minus_btn = card.getElementsByTagName("a")[2];
            minus_btn.onclick = Function(`btn_minus_value(${i})`)
        }
    }

    function getList() {
        var return_list = []

        var menu_table = myTable_val.toString();
        var cards = document.getElementsByClassName("card-wrapper");
        for(var i = 0; i < cards.length; i++){
            var card = cards[i];
            var value_btn = card.getElementsByTagName("a")[1];
            var count = parseInt(value_btn.innerText);
            if(count > 0){
                var menu_name = card.getElementsByTagName("h4")[0].innerText;
                var menu_value = count.toString();
                return_list.push({
                    "menu": menu_name,
                    "value": menu_value,
                    "table": menu_table
                })
            }
        }

        return return_list;
    }

    function clear_cards() {
        var cards = document.getElementsByClassName("card-wrapper");
        for(var i = 0; i < cards.length; i++){
            var card = cards[i];
            var value_btn = card.getElementsByTagName("a")[1];
            value_btn.innerText = "0";
        }
    }

    function load_menu() {
        var token = {
            'token': 'test_token'
        }
        $.ajax({
            type: "GET",
            async: true,
            dataType: "json",
            url: "/poster",
            data: token,
            success: function(data) {
                VmenuSection.updateMenuView(data['base-root']['menus-init'])
                setTimeout(() => {
                    addClickEvent_forAllCounterBtn()
                }, 0);
            }
        });
    }

    $(".btn-success").click(function() {

        var requests_list = getList();
        if(requests_list.length === 0){
            alert("尚未選擇餐點");
            return;
        }
        
        var check_msg = "請問您確定要送出一下餐點嗎?\n";
        for(var i = 0; i < requests_list.length; i++){
            var menu_str = requests_list[i]["menu"];
            var val_str = requests_list[i]["value"];
            check_msg += "\n" + menu_str + "  " + val_str + "個";
        }
        var user_check_window = confirm(check_msg);
        if(!user_check_window){
            return;
        }

        var rootJson = JSON.stringify({
            "base-root":
            {
                "menu-requests": requests_list
            }
        });

        $.ajax({
            type: "POST",
            async: true,
            dataType: "text",
            url: "/poster",
            contentType: 'application/json;',
            data: rootJson,
            success: function(msg) {
                if(msg != "OK"){
                    alert("傳輸失敗");
                }

                clear_cards();
                myMoney_val = 0;
                moneyView_updata();
            }
        });
    });

    load_menu();
});