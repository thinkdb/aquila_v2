(function (jq) {
    /*
    用于保存当前作用域内的"全局变量"
     */
    var NB_GLOBAL_DICT = {};

    /*
    用于向后台发送请求的url
     */
    var requestUrl;

    // 为字符串创建format方法，用于字符串格式化
    String.prototype.format = function (args) {
        return this.replace(/\{(\w+)\}/g, function (s, i) {
            return args[i];
        });
    };

    /*
     CSRF配置
     */
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    /*
     全局Ajax中添加请求头X-CSRFToken，用于跨过CSRF验证
     */
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });


    function saveData() {
        // 退出编辑模式
        if ($('#edit_mode_target').hasClass('btn-warning')) {
            $.TableEditMode('#edit_mode_target', '#table_body', null, null);
        }

        // 获取被修改过的数据
        var updateData = [];
        $('#table_body').children().each(function () {
            var rows = {};
            var nid = $(this).attr('nid');
            var num = $(this).attr('num');

            var flag = false;
            $(this).children('td[edit-enable="true"]').each(function () {
                var original = $(this).attr('original');
                var name = $(this).attr('name');
                var newer;
                if ($(this).attr('edit-type') == 'input') {
                    newer = $(this).text();

                } else if ($(this).attr('edit-type') == 'select') {
                    newer = $(this).attr('id');
                }
                if (newer != undefined && original != newer) {
                    rows[name] = newer;
                    flag = true;
                }
            });
            if (flag) {
                rows["nid"] = nid;
                rows["num"] = num;
                updateData.push(rows);
            }
        });
        if (updateData.length < 1) {
            return;
        }
        updateData = JSON.stringify(updateData);

        $.ajax({
            url: requestUrl,
            type: 'PUT',
            data: {update_list: updateData},
            success: function (response) {
                if (response.status) {
                    SuccessHandleStatus(response.message);
                } else {
                    ErrorHandleStatus(response.message, response.error);
                }
                refreshData();

            },
            error: function () {
                alert('请求异常');
            }
        })
    }

    function refreshData() {
        var currentPage = $('#pager').find("li[class='active']").text();
        initialize(currentPage);
    }

    function deleteData() {
        var id_list = [];
        $('#table_body').find(':checkbox').each(function () {
            if ($(this).prop('checked')) {
                id_list.push($(this).val());
            }
        });
        $.ajax({
            url: requestUrl,
            type: 'DELETE',
            data: {id_list: id_list},
            traditional: true,
            success: function (response) {
                if (response.status) {
                    SuccessHandleStatus(response.message);
                } else {
                    alert(response.message);
                }
                $.Hide('#shade,#modal_delete');
                refreshData();

            },
            error: function () {
                $.Hide('#shade,#modal_delete');
                alert('请求异常');
            }
        })
    }

    /*
     绑定头部按钮事件
     */
    function bindMenuFunction() {
        $('#edit_mode_target').click(function () {
            $.TableEditMode(this, '#table_body', null, null)
        });

        $('#check_all').click(function () {
            $.CheckAll('#table_body', null);
        });

        $('#check_cancel').click(function () {
            $.UnCheckAll('#table_body', null);
        });

        $('#check_reverse').click(function () {
            $.ReverseCheck('#table_body', null, null)
        });

        $('#do_delete').click(function () {
            $.Show('#shade,#modal_delete');
        });
        $('#do_delete_confirm').click(function () {
            deleteData();
        });

        $('#do_save').click(function () {
            saveData();
        });

        $('#do_refresh').click(function () {
            refreshData();
        });

    }

    /*
     绑定搜索条件的事件
     */
    function bindSearchCondition() {
        bindChangeSearchCondition();
        bindSubmitSearchCondition();
    }

    /*
     聚合搜索条件
     */
    function aggregationSearchCondition() {
        var ret = {};
        $("#search_conditions").children().each(function () {
            var $condition = $(this).find("input[is-condition='true'],select[is-condition='true']");
            var name = $condition.attr('name');
            var value = $condition.val();
            if (!$condition.is('select')) {
                name = name + "__contains";
            }
            if (value) {
                var valList = $condition.val().trim().replace('，', ',').split(',');
                if (ret[name]) {
                    ret[name] = ret[name].concat(valList);
                } else {
                    ret[name] = valList;
                }
            }
        });
        return ret;
    }

    /*
     页面初始化（获取数据，绑定事件）
     */
    function initialize(pager) {
        $.Show('#shade,#loading');
        var conditions = JSON.stringify(aggregationSearchCondition());
        var $body = $('#table_body');
        $.ajax({
            url: requestUrl,
            type: 'GET',
            traditional: true,
            data: {'condition': conditions, 'pager': pager},
            dataType: 'JSON',
            success: function (response) {
                $.Hide('#shade,#loading');
                if (response.status) {
                    initGlobal(response.data.global_dict);
                    initTableHeader(response.data.table_config);
                    initTableBody(response.data.page_info.page_start, response.data.data_list, response.data.table_config);
                    initPager(response.data.page_info.page_str);
                    initSearchCondition(response.data.condition_config);
                    $.BindDoSingleCheck('#table_body', null, null);
                } else {
                    alert(response.message);
                }
            },
            error: function () {
                $.Hide('#shade,#loading');
            }
        })

    }

    /*
     初始化全局变量
     */
    function initGlobal(globalDict) {
        $.each(globalDict, function (k, v) {
            NB_GLOBAL_DICT[k] = v;
        })
    }

    /*
     初始化表格的头部
     */
    function initTableHeader(tbConfig) {
        var $header = $('#table_head');

        $header.find('th').remove();

        // 创建“选择列”
        var ck = document.createElement('th');
        ck.innerText = '选择';
        $header.find('tr').append(ck);

        // 创建“序号列”
        var num = document.createElement('th');
        num.innerText = '序号';
        $header.find('tr').append(num);


        $.each(tbConfig, function (k, item) {
            if (item.display) {
                var tag = document.createElement('th');
                tag.innerText = item.title;
                $header.find('tr').append(tag);
            }
        });
    }

    /*
     初始化表格内容
     */
    function initTableBody(startNum, list, tbConfig) {
        var $body = $('#table_body');
        $body.empty();


        $.each(list, function (k1, row) {
            // row 表示从数据库获取的每行资产字典信息 {'id':'1','name': 'root' ...}
            // tbConfig 包含了所有表格的配置

            var tr = document.createElement('tr');
            tr.setAttribute('nid', row['id']);
            tr.setAttribute('num', startNum + k1 + 1);
            // 创建每一行的CheckBox
            var tagTd = document.createElement('td');
            var tagCheckBox = document.createElement('input');
            tagCheckBox.type = 'checkbox';
            tagCheckBox.value = row['id'];
            $(tagTd).append(tagCheckBox);
            $(tr).append(tagTd);
            // 创建每一行的CheckBox
            var tagNum = document.createElement('td');
            tagNum.innerHTML = startNum + k1 + 1;
            $(tr).append(tagNum);


            $.each(tbConfig, function (k2, config) {
                // config中是对每一列数据的展示方式
                if (config.display) {

                    var td = document.createElement('td');

                    // 创建td的内容
                    var kwargs = {};
                    $.each(config.text.kwargs, function (k, v) {
                        if (v.startsWith('@@')) {
                            var global_name = v.substring(2, v.length);
                            kwargs[k] = getNameByGlobalList(global_name, row[config.q]);
                        } else if (v.startsWith('@')) {
                            kwargs[k] = row[v.substring(1, v.length)]
                        } else {
                            kwargs[k] = v;
                        }
                    });
                    td.innerHTML = config.text.content.format(kwargs);

                    // 创建td的属性
                    $.each(config.attr, function (k, v) {
                        if (v.startsWith('@')) {
                            td.setAttribute(k, row[v.substring(1, v.length)]);
                        } else {
                            td.setAttribute(k, v);
                        }
                    });

                    $(tr).append(td);
                }
            });
            $body.append(tr);
        })
    }

    /*
     根据ID从全局变量中获取其对应的内容
     */
    function getNameByGlobalList(globalName, itemId) {
        var result;
        $.each(NB_GLOBAL_DICT[globalName], function (k, v) {
            if (v.id == itemId) {
                result = v.name;
                return false;
            }
        });
        return result;
    }

    /*
     初始化分页内容
     */
    function initPager(pageStr) {
        var $pager = $('#pager');
        $pager.empty();
        $pager.append(pageStr);
    }

    /*
     初始化搜索条件
     */
    function initSearchCondition(config) {
        var $search_condition = $('#search_condition');
        if ($search_condition.attr('init') == 'true') {
            return
        }
        if (config.length > 0) {
            var first_item = config[0];
            initDefaultSearchCondition(first_item);
        }

        $.each(config, function (k, v) {
            var condition_type = v['condition_type'];
            var tag = document.createElement('li');
            var a = document.createElement('a');
            a.innerHTML = v['text'];
            $(tag).append(a);
            tag.setAttribute('name', v['name']);
            tag.setAttribute('condition-type', condition_type);
            if (condition_type == 'select') {
                tag.setAttribute('global-name', v['global_name']);
            }
            $('#search_condition').find('ul').append(tag);
        });
        $search_condition.attr('init', 'true');
    }

    /*
     初始化默认的第一个条件
     */
    function initDefaultSearchCondition(item) {

        var tag;
        if (item.condition_type == 'input') {
            tag = $.CreateInput({
                'is-condition': 'true',
                'class': 'form-control no-radius',
                'name': item.name,
                'placeholder': '逗号分割多条件'
            }, {});
        } else if (item.condition_type == 'select') {
            tag = $.CreateSelect({
                'is-condition': 'true',
                'class': 'form-control select-icon no-radius',
                'name': item.name
            }, {}, NB_GLOBAL_DICT[item.global_name], null, 'id', 'name');
        }
        var $current = $('#search_condition');
        $current.children().first().text(item.text);
        $current.after(tag);

    }

    /*
     绑定修改条件之后的事件
     */
    function bindChangeSearchCondition() {
        $('#search_condition').find('ul').delegate('li', 'click', function () {
            var name = $(this).attr('name');
            var text = $(this).text();
            var condition_type = $(this).attr('condition-type');
            var global_name = $(this).attr('global-name');
            var tag;
            if (condition_type == 'input') {
                tag = $.CreateInput({
                    'is-condition': 'true',
                    'class': 'form-control no-radius',
                    'name': name,
                    'placeholder': '逗号分割多条件'
                }, {});
            } else if (condition_type == 'select') {
                tag = $.CreateSelect({
                    'is-condition': 'true',
                    'class': 'form-control select-icon no-radius',
                    'name': name
                }, {}, NB_GLOBAL_DICT[global_name], null, 'id', 'name');
            }
            var $current = $(this).parent().parent();
            $current.children().first().text(text);
            $current.next().remove();
            $current.after(tag);

        });
    }

    /*
     绑定提交搜索按钮
     */
    function bindSubmitSearchCondition() {
        $('#search_condition_submit').click(function () {
            initialize(1);
        });
    }

    /*
     更新资产错误，显示错误信息
     */
    function ErrorHandleStatus(content, errorList) {
        var $handle_status = $('#handle_status');
        $handle_status.attr('data-toggle', 'popover');

        var errorStr = '';
        $.each(errorList, function (k, v) {
            errorStr = errorStr + v.num + '. ' + v.message + '</br>';
        });

        $handle_status.attr('data-content', errorStr);
        $handle_status.popover();

        var msg = "<i class='fa fa-info-circle'></i>" + content;
        $handle_status.empty().removeClass('btn-success').addClass('btn-danger').html(msg);

    }

    /*
     更新资产成功，显示更新信息
     */
    function SuccessHandleStatus(content) {
        var $handle_status = $('#handle_status');
        $handle_status.popover('destroy');
        var msg = "<i class='fa fa-check'></i>" + content;
        $handle_status.empty().removeClass('btn-danger').addClass('btn-success').html(msg);
        setTimeout(function () {
            $handle_status.empty().removeClass('btn-success btn-danger');
        }, 5000);
    }

    /*
     监听是否已经按下control键
     */
    window.globalCtrlKeyPress = false;
    window.onkeydown = function (event) {
        if (event && event.keyCode == 17) {
            window.globalCtrlKeyPress = true;
        }
    };

    window.onkeyup = function (event) {
        if (event && event.keyCode == 17) {
            window.globalCtrlKeyPress = false;
        }
    };

    /*
     按下Control，联动表格中正在编辑的select
     */
    function bindMultiSelect() {
        $('#table_body').delegate('select', 'change', function () {
            if (window.globalCtrlKeyPress) {
                var index = $(this).parent().index();
                var value = $(this).val();
                $(this).parent().parent().nextAll().find("td input[type='checkbox']:checked").each(function () {
                    $(this).parent().parent().children().eq(index).children().val(value);
                });
            }
        });

    }


    /* ================= */

    function DoTrIntoEdit($tr, specialInEditFunc) {
        $tr.find('td[edit-enable="true"]').each(function () {
            ExecuteTdIntoEdit($(this), specialInEditFunc);
        });
    }

    function DoTrOutEdit($tr, specialOutEditFunc) {
        $tr.find('td[edit-enable="true"]').each(function () {
            ExecuteTdOutEdit($(this), specialOutEditFunc);
        });
    }

    function ExecuteTdIntoEdit($td, specialInEditFunc) {
        var editType = $td.attr('edit-type');

        if (editType == 'input') {
            var text = $td.text();
            $td.addClass('padding-3');
            var htmlTag = $.CreateInput({'value': text, 'class': 'padding-tb-5 form-control '}, {'width': '100%'});
            $td.empty().append(htmlTag);
        } else if (editType == 'select') {
            var globalName = $td.attr('global-name');
            var selectedId = $td.attr('id');
            if (specialInEditFunc) {
                specialInEditFunc($td, globalName, selectedId);
            } else {
                $td.addClass('padding-3');
                var htmlTag = $.CreateSelect(
                    {'class': 'padding-tb-5 form-control'},
                    {'width': '100%'},
                    NB_GLOBAL_DICT[globalName],
                    selectedId,
                    'id',
                    'name'
                );
                $td.empty().append(htmlTag);
            }
        }

    }

    function ExecuteTdOutEdit($td, specialOutEditFunc) {
        var editType = $td.attr('edit-type');

        if (editType == 'input') {
            var text = $td.children().first().val();
            $td.removeClass('padding-3');
            $td.empty().text(text);
        } else if (editType == 'select') {
            var globalName = $td.attr('global-name');

            if (specialOutEditFunc) {
                specialOutEditFunc($td, globalName);
            }
            else {
                $td.removeClass('padding-3');
                var selecting_val = $td.children().first().val();
                var selecting_text = $td.children().first().find("option[value='" + selecting_val + "']").text();
                $td.empty().html(selecting_text);
                $td.attr('id', selecting_val);
            }
        }
    }

    jq.extend({
        'initMenu': function (target) {
            $(target).addClass('active').siblings().removeClass('active');
        },
        'CreateTd': function (attrs, csses, text) {
            var obj = document.createElement('td');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            $(obj).html(text);
            return obj;
        },
        'CreateTds': function (attrs, csses, list, seprate) {
            var obj = document.createElement('td');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            $.each(list, function (k, v) {
                if (k == 0) {
                    $(obj).append(v);
                } else {
                    $(obj).append(seprate);
                    $(obj).append(v);
                }
            });
            return obj;
        },
        'CreateTr': function (attrs, csses, tds) {
            var obj = document.createElement('tr');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            $.each(tds, function (k, v) {
                $(v).appendTo($(obj));
            });
            return obj;
        },
        'CreateInput': function (attrs, csses) {
            var obj = document.createElement('input');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            return obj
        },
        'CreateA': function (attrs, csses, text) {
            var obj = document.createElement('a');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            $(obj).html(text);
            return obj
        },
        'CreateOption': function (attrs, csses, text) {
            var obj = document.createElement('option');
            $.each(attrs, function (k, v) {
                $(obj).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(obj).css(k, v);
            });
            $(obj).html(text);
            return obj
        },

        /*
         创建Select标签
         options: 必须是含有id和name的对象，id作为option的value，name作为option的内容，例：obj.id = 1,obj.name = 'China'
         current: 当前被选中的内容，例：current ＝ 'China'
         key_value,key_text是全局字典的key和value的key
         */
        'CreateSelect': function (attrs, csses, option_data_list, current_value, key_value, key_text) {
            var sel = document.createElement('select');
            $.each(attrs, function (k, v) {
                $(sel).attr(k, v);
            });
            $.each(csses, function (k, v) {
                $(sel).css(k, v);
            });
            $.each(option_data_list, function (k, v) {
                var opt1 = document.createElement('option');
                var sel_text = v[key_text];
                var sel_value = v[key_value];
                if (sel_value == current_value) {
                    $(opt1).text(sel_text).attr('value', sel_value).attr('text', sel_text).appendTo($(sel));
                    $(opt1).prop('selected', true);
                } else {
                    $(opt1).text(sel_text).attr('value', sel_value).attr('text', sel_text).appendTo($(sel));
                }
            });
            return sel;
        },


        /*
         搜索插件 -> 添加搜索条件
         ths:点击的当前对象
         */
        'AddSearchCondition': function (ths) {
            var $duplicate = $(ths).parent().parent().clone(true);
            $duplicate.find('.fa-plus-square').addClass('fa-minus-square').removeClass('fa-plus-square');
            $duplicate.find('a[onclick="$.AddSearchCondition(this)"]').attr('onclick', "$.RemoveSearchCondition(this)");

            $duplicate.appendTo($(ths).parent().parent().parent());
        },

        /*
         搜索插件 -> 移除当前搜索条件
         ths:点击的当前对象
         */
        'RemoveSearchCondition': function (ths) {
            $(ths).parent().parent().remove();
        },

        'Hide': function (target) {
            $(target).addClass('hide');
        },

        'Show': function (target) {
            $(target).removeClass('hide');
        },
        /*
         表格CheckBox全选
         tableBody:表格中body选择器对象
         rowEditFunc:行进入编辑模式的特殊函数处理，例如：状态、等不同的样式
         */
        'CheckAll': function (tableBody, specialInEditFunc) {

            if ($(tableBody).attr('edit-mode') == 'true') {
                $(tableBody).find(':checkbox').each(function () {
                    var check = $(this).prop('checked');
                    var disabled = $(this).prop('disabled');
                    var $tr = $(this).parent().parent();
                    if (!check && !disabled) {
                        $tr.addClass('success');
                        $(this).prop('checked', true);
                        DoTrIntoEdit($tr, specialInEditFunc);
                    }
                });
            } else {
                $(tableBody).find(':checkbox').each(function () {
                    var disabled = $(this).prop('disabled');
                    if (!disabled) {
                        $(this).prop('checked', true);
                    }
                });
            }
            //$(tableBody).find(':checkbox').prop('checked',true);
        },

        /*
         表格CheckBox取消选择
         tableBody:表格中body选择器对象
         */
        'UnCheckAll': function (tableBody, specialOutEditFunc) {


            if ($(tableBody).attr('edit-mode') == 'true') {
                $(tableBody).find(':checkbox').each(function () {
                    var check = $(this).prop('checked');
                    var $tr = $(this).parent().parent();
                    if (check) {
                        $tr.removeClass('success');
                        DoTrOutEdit($tr, specialOutEditFunc);
                    }
                });
            }

            $(tableBody).find(':checkbox').prop('checked', false);
        },

        /*
         表格CheckBox反选
         targetContainer:表格中body选择器对象
         specialInEditFunc:
         specialOutEditFunc:
         */
        'ReverseCheck': function (tableBody, specialInEditFunc, specialOutEditFunc) {
            $(tableBody).find(':checkbox').each(function () {
                var check = $(this).prop('checked');
                var disabled = $(this).prop('disabled');
                var $tr = $(this).parent().parent();
                if (check) {
                    $(this).prop('checked', false);
                    if ($(tableBody).attr('edit-mode') == 'true') {
                        $tr.removeClass('success');
                        DoTrOutEdit($tr, specialOutEditFunc);
                    }
                } else {
                    if (!disabled) {
                        $(this).prop('checked', true);
                    }
                    if ($(tableBody).attr('edit-mode') == 'true' && !disabled) {
                        $tr.addClass('success');
                        //this row enable edit
                        DoTrIntoEdit($tr, specialInEditFunc);
                    }

                }
            })
        },

        /*
         绑定点击CheckBox事件
         targetContainer:表格中body选择器对象
         specialInEditFunc:
         specialOutEditFunc:
         */
        'BindDoSingleCheck': function (tableBody, specialInEditFunc, specialOutEditFun) {
            $(tableBody).delegate(':checkbox', 'click', function () {
                var $tr = $(this).parent().parent();
                if ($(this).prop('checked')) {
                    if ($(tableBody).attr('edit-mode') == 'true') {
                        //this row switch in edit mode
                        $tr.addClass('success');
                        DoTrIntoEdit($tr, specialInEditFunc);
                    }
                } else {
                    if ($(tableBody).attr('edit-mode') == 'true') {
                        //this row switch out edit mode
                        $tr.removeClass('success');
                        DoTrOutEdit($tr, specialOutEditFun);
                    }
                }

            });
        },

        /*
         表格进入编辑模式
         ths:当前点击的按钮
         body:表格中body选择器对象
         */
        'TableEditMode': function (ths, body, specialInEditFunc, specialOutEditFunc) {
            if ($(ths).hasClass('btn-warning')) {
                $(ths).removeClass('btn-warning').find('span').text('进入编辑模式');

                $(body).attr('edit-mode', 'false');

                $(body).children().removeClass('success');

                $(body).find(':checkbox').each(function () {
                    var check = $(this).prop('checked');
                    var $tr = $(this).parent().parent();
                    if (check) {
                        $tr.removeClass('success');
                        DoTrOutEdit($tr, specialOutEditFunc);
                    }
                });

            } else {
                //into edit mode
                $(ths).addClass('btn-warning').find('span').text('退出编辑模式');
                $(body).attr('edit-mode', 'true');

                $(body).find(':checkbox').each(function () {
                    var check = $(this).prop('checked');
                    var $tr = $(this).parent().parent();
                    if (check) {
                        $tr.addClass('success');
                        DoTrIntoEdit($tr, specialInEditFunc);
                    }
                });
            }
        },

        /*
         tab菜单(例如：$.BindTabMenu('#tab-menu-title', '#tab-menu-body');)
         */
        'BindTabMenu': function (title, body) {
            $(title).children().bind("click", function () {
                var $menu = $(this);
                var $content = $(body).find('div[content="' + $(this).attr("content-to") + '"]');
                $menu.addClass('current').siblings().removeClass('current');
                $content.removeClass('hide').siblings().addClass('hide');
            });
        },

        'nbDataList': function(url){
            requestUrl = url;
            initialize(1);
            bindMenuFunction();
            bindMultiSelect();
            bindSearchCondition();
        }

    });
})(jQuery);