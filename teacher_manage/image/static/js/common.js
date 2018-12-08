var image = $('#image');
var is_first = true;
var select_data = {'stu_id': '', 'stu_name': '', 'stu_class': '', 'type': '', 'year': ''};
// Get the Viewer.js instance after initialized
image.viewer({
    inline: true,
    viewed: function () {
        image.viewer('zoomTo', 1);
    }
});
var viewer = image.data('viewer');
console.log(viewer);
var get_new = $('#get-new');
var flush_data = $('#flush');
var log_out = $('#log-out');


function search() {
    var stuNumber = $('input[name="stuNumber"]').val();
    var stuName = $('input[name="stuName"]').val();
    var type = $("#type").val();
    var stuClass = $("#theClass").val();
    var year = $('#year').val();
    // alert("状态：" + type + "班级：" + stuClass + "学号：" + stuNumber + "姓名：" + stuName);
    getData(1, stuName, stuClass, stuNumber, type, year);
    // 向后台发送请求时就用上面的值
    select_data['stu_id'] = stuNumber;
    select_data['stu_name'] = stuName;
    select_data['stu_class'] = stuClass;
    select_data['type'] = type;
    select_data['year'] = year;
}

function changeType(id) {
    //var _this = $(".activType:eq("+i+")");
    var _this = $("#type" + id);
    //var score = _this.val();
    var score = _this.children("option:selected").attr('name');
    // alert(hh);
    //_this.parents("td").siblings(".score").html(score);
    _this.parents("td").siblings(".score").children("input").val(score);
    //var hh = $(this).parents("td").find(".activType").val();
};

function get_classes() {
    $.ajax({
        type: "GET",
        dataType: "JSON",
        url: "/classes",
        success: function (result) {
            var all_class_name = result.classes;
            var classes_html = '<option value="" selected="selected">请选择</option>';
            for (var i = 0; i < all_class_name.length; i++) {
                if (select_data.stu_class == all_class_name[i]) {
                    classes_html += '<option value="' + all_class_name[i] + '" selected="selected">' + all_class_name[i] + '</option>';
                } else {
                    classes_html += '<option value="' + all_class_name[i] + '">' + all_class_name[i] + '</option>';
                }
            }
            $('#theClass').html(classes_html)
        },
        error: function (result) {
            alert('获取班级列表失败！http code:' + result.status);
        }
    })
}

function get_years() {
    $.ajax({
        type: "GET",
        dataType: "JSON",
        url: "/years",
        success: function (result) {
            var all_year_name = result.years;
            var classes_html = '<option value="" selected="selected">全部</option>';
            for (var i = 0; i < all_year_name.length; i++) {
                if (select_data.year == all_year_name[i]) {
                    classes_html += '<option value="' + all_year_name[i] + '" selected="selected">' + all_year_name[i] + '</option>';
                } else {
                    classes_html += '<option value="' + all_year_name[i] + '">' + all_year_name[i] + '</option>';
                }
            }
            $('#year').html(classes_html)
        },
        error: function (result) {
            alert('获取班级列表失败！http code:' + result.status);
        }
    })
}

//获取数据
function getData(page, stuName, stuClass, stuNumber, type, year) {
    get_classes();
    get_years();
    if (page === undefined) {
        page = 1;
    }
    if (stuName === undefined) {
        stuName = '';
    }
    if (stuClass === undefined) {
        stuClass = '';
    }
    if (stuNumber === undefined) {
        stuNumber = '';
    }
    if (type === undefined) {
        type = '';
    }

    if (year === undefined) {
        year = '';
    }

    $('#table').html('');
    $.ajax({
        type: "GET",
        dataType: "JSON",
        cache: false,
        url: "/shenpi",
        data: {
            'page': page, 'stu_name': stuName, 'type': type,
            'stu_class': stuClass, 'stu_id': stuNumber, 'year': year,
        },
        success: function (result) {
            var totalData = result.apply_info.data;
            var html = '';
            var now_page = result.apply_info.page_num;
            var max_page = result.apply_info.max_page_num;
            $.each(totalData, function (i, obj) {
                html += '<tr>';
                html += '<td class="stuNum"><div><strong>' + obj.stu_id + '</strong></div><br><div class="small" style=" color: grey">' + obj.apply_year + '</div></td>';
                html += '<td><strong><div data-toggle="tooltip" title="'+obj.stu_class+'">' + obj.stu_name + '</div></strong></td>';
                try {
                    if (obj.apply_category.length === 0) {
                        html += '<td class="findOption"><span class="activName" data-toggle="tooltip" title="【' + obj.apply_category + '】">' + obj.apply_category + '</span><br>';
                    } else {
                        html += '<td class="findOption"><span class="activName" data-toggle="tooltip" title="【' + obj.apply_category + '】">' + obj.apply_content + '</span><br>';
                    }
                } catch (e) {
                    console.log(e);
                    console.log(obj);
                }

                try {
                    if (obj.options.length != 0) {
                        html += '<select class="activType" id="type' + obj.apply_id + '" onchange="changeType(' + obj.apply_id + ')">';
                        $.each(obj.options, function (j, item) {
                            if (item.selected) {
                                html += '<option selected="true" name="' + item.option_score + '" value="' + item.option_id + '">' + item.option_name + '</option>';
                            } else {
                                html += '<option name="' + item.option_score + '" value="' + item.option_id + '">' + item.option_name + '</option>';
                            }
                        });
                        html += '</select>';
                        //html += '<br><div class="Category">【' + obj.apply_category + '】</div></td>';
                    }
                } catch (e) {
                    console.log(e);
                    console.log(obj);
                }
                if (obj.apply_type === '智育') {
                    html += '<td class="text-success"><strong>' + obj.apply_type + '</strong></td>';
                } else {
                    html += '<td>' + obj.apply_type + '</td>';
                }

                if (obj.changeable) {
                    html += '<td class="score"><input class="form-control" type="number" max="' + obj.max_score + '" min="' + obj.min_score + '" data-toggle="tooltip" name="scoreInput" title="1-' + obj.max_score + '分" value="' + obj.apply_score + '"/></td>';
                } else {
                    html += '<td class="score"><input class="form-control" type="number" name="scoreInput" disabled="disabled" value="' + obj.apply_score + '"/></td>';
                }
                if (obj.apply_image == null) {
                    html += '<td>用户没有上传图片</td>';
                } else {
                    html += '<td><img class="theImg" alt="' + obj.stu_name + '-' + obj.apply_content + '" src="' + obj.apply_image + '" onerror="this.src = \'/image/static/image/404.jpg\'"/></td>';
                }
                if (obj.apply_status.indexOf('通过') !== -1) {
                    html += '<td class="judge-type judge-pass">' + obj.apply_status + '</td>';
                } else if (obj.apply_status.indexOf('打回') !== -1) {
                    html += '<td class="judge-type judge-refuse">' + obj.apply_status + '</td>';
                } else {
                    html += '<td class="judge-type">' + obj.apply_status + '</td>';
                }
                if(obj.judge_content !== undefined || obj.judge_content !== null || obj.judge_content !== ''){
                    html += '<td><textarea class="form-control">'+obj.judge_content+'</textarea></td>';
                }else{
                    html += '<td><textarea class="form-control">同意</textarea></td>';
                }
                html += '<td><button type="button" name="' + obj.apply_id + '" class="btn btn-success btn-sm pass">通过</button>&nbsp;<button type="button" name="' + obj.apply_id + '" class="btn btn-danger btn-sm refuse">打回</button></td></tr>';
            });
            $('#table').html(html);
            if (is_first) {
                // View a list of images
                $('#table').viewer();
                is_first = false;
            } else {
                $('#table').viewer('update');
            }
            var page_html = '';
            if (now_page === 1) {
                page_html += '<li class="disabled text-info"><a>&laquo;</a></li>'
            } else if (now_page > 1) {
                page_html += '<li class="thePage" data-page="1"><a href="#">&laquo;</a></li>'
            }
            for (let page = 1; page <= max_page; page++) {
                if (page < now_page - 5) {
                    continue
                }
                if (page === now_page) {
                    page_html += '<li class="thePage active" data-page="' + page + '"><a>' + page + '</a></li>'
                } else {
                    page_html += '<li class="thePage" data-page="' + page + '"><a>' + page + '</a></li>'
                }
                if (page > now_page + 10) {
                    break;
                }
            }
            if (now_page === max_page) {
                page_html += '<li class="disabled text-info"><a>&raquo;</a></li>'
            } else if (now_page < max_page) {
                page_html += '<li class="thePage" data-page="' + max_page + '"><a href="#">&raquo;</a></li>'
            }
            $('#pagination').html(page_html);
            $(function () {
                $("[data-toggle='tooltip']").tooltip();
            });
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert('获取列表失败！http code: ' + XMLHttpRequest.status);
            // console.log(XMLHttpRequest);
            alert(textStatus);
            // alert(errorThrown);
        }
    })
};

$(function () {
    $(document).on('click', '.pass', function () {
        var applyId = $(this).attr('name');
        var stuId = $(this).parent('td').siblings(".stuNum").find('strong').html();
        var optionId = $(this).parent('td').siblings(".findOption").find(".activType").val();
        var Score = $(this).parent('td').siblings('.score').children('input[name="scoreInput"]').val();
        var examContent = $(this).parent("td").prev('td').children("textarea").val();
        var examType = 'pass';
        var this_btn = $(this);
        this_btn.append(' <span class="fa fa-spin fa-spinner"></span>');
        var judge_type = $(this).parent("td").parent("tr").children('.judge-type');
        var refuse_btn = $(this).parent("td").children(".refuse");
        $.ajax({
            type: 'POST',
            url: '/operation',
            data: {
                apply_id: applyId,
                stu_id: stuId,
                option_id: optionId,
                apply_score: Score,
                examine_content: examContent,
                examine_type: examType
            },
            dataType: 'json',
            success: function (data) {
                if (data.status === 'success') {
                    this_btn.html('已通过 <span class="fa fa-check-circle-o fa-lg"></span>');
                    if (judge_type.hasClass('judge-refuse')) {
                        judge_type.removeClass('judge-refuse');
                    }
                    judge_type.addClass('judge-pass');
                    judge_type.html('审批通过');
                    refuse_btn.html('打回');
                } else {
                    this_btn.html('再次通过');
                    alert('审批通过失败: ' + data.msg);
                }

            },
            error: function (data) {
                this_btn.html('再次通过');
                alert('提交失败！http code: ' + data.status);
            }
        });
    });

    $(document).on('click', '.refuse', function () {
        var applyId = $(this).attr('name');
        var stuId = $(this).parent('td').siblings(".stuNum").find('strong').html();
        var optionId = $(this).parent('td').siblings(".findOption").find(".activType").val();
        var Score = $(this).parent('td').siblings(".score").children('input[name="scoreInput"]').val();
        var examContent = $(this).parent("td").prev('td').children("textarea").val();
        var examType = 'refuse';
        var this_btn = $(this);
        this_btn.append(' <span class="fa fa-spin fa-spinner"></span>');
        var judge_type = $(this).parent("td").parent('tr').children('.judge-type');
        var pass_btn = $(this).parent("td").children(".pass");
        console.log(judge_type);
        $.ajax({
            type: 'POST',
            url: '/operation',
            data: {
                apply_id: applyId,
                stu_id: stuId,
                option_id: optionId,
                apply_score: Score,
                examine_content: examContent,
                examine_type: examType
            },
            dataType: 'json',
            success: function (data) {
                if (data.status === 'success') {
                    this_btn.html('已打回 <span class="fa fa-check-circle-o fa-lg"></span>');
                    if (judge_type.hasClass('judge-pass')) {
                        judge_type.removeClass('judge-pass');
                    }
                    judge_type.addClass('judge-refuse');
                    judge_type.html('审批打回');
                    pass_btn.html('通过');
                } else {
                    this_btn.html('再次打回');
                    alert('审批打回失败: ' + data.msg);
                }
            },
            error: function (data) {
                this_btn.html('再次打回');
                alert('打回失败！http code: ' + data.status);
            }
        });
    });

    $(document).on('click', '.thePage', function () {
        $(this).addClass("active");
        $(this).siblings('li').removeClass("active");
        var page = $(this).attr("data-page");
        // alert(page);
        getData(page, select_data.stu_name, select_data.stu_class, select_data.stu_id, select_data.type, select_data.year)
    });

    $(document).on('click', '#get-new', function () {
        get_new_data();
    });
    $(document).on('click', '#flush', function () {
        flush_db();
    });
    $(document).on('click', '#log-out', function () {
        logout();
    });
    $(document).on('click', '#xls', function () {
        export2excel('xls');
    });
    $(document).on('click', '#xlsx', function () {
        export2excel('xlsx');
    });
});

$(document).ready(function () {
    getData();
});

function flush_db() {
    if (confirm("你确定要清空数据库的信息吗？")) {
        flush_data.html('删除中...');
        flush_data.addClass('disabled');
        $.ajax({
            type: 'GET',
            url: '/flush_db',
            dataType: 'json',
            success: function (data) {
                if (data.status) {
                    alert('清空成功！点击返回主页');
                    window.location.href = '/'
                } else {
                    alert('清除失败！:' + data.msg);
                }
                flush_data.html('清空数据库数据');
                flush_data.removeClass('disabled');
            },
            error: function (data) {
                alert('清空请求失败！http code:' + data.status);
                flush_data.html('清空数据库数据');
                flush_data.removeClass('disabled');
            }
        });
    }
}

function logout() {
    if (confirm("你确定要退出登录吗？")) {
        $.ajax({
            type: 'GET',
            url: '/logout',
            dataType: 'json',
            success: function (data) {
                if (data.status) {
                    alert('退出成功！点击返回主页');
                    window.location.href = '/'
                } else {
                    alert('退出失败！:' + data.msg + '请直接用另一个浏览器登录');
                }
            },
            error: function (data) {
                alert('退出请求失败！http code:' + data.status);
            }
        });
    }
}

function get_new_data() {
    if (confirm("你确定要获取最新的数据吗？用时可能会比较长。")) {
        get_new.html('正在爬取最新申请...');
        get_new.addClass('disabled');
        $.ajax({
            type: 'GET',
            url: '/get_new_data',
            dataType: 'json',
            success: function (data) {
                if (data.status) {
                    alert('最新申请全部下载成功！刷新页面即可看到');
                    $('#get-new').html('获取最新数据');
                } else {
                    alert('清除失败！:' + data.msg);
                }
                get_new.html('获取最新数据');
                get_new.removeClass('disabled');
            },
            error: function (data) {
                alert('清空请求失败！http code:' + data.status);
                get_new.html('获取最新数据');
                get_new.removeClass('disabled');
            }
        });
    }
}

function export2excel(export_type) {
    window.open('/export?stu_name'+ select_data.stu_name +'&type='+ select_data.type +'&export_type='+export_type+
        '&stu_class='+ select_data.stu_class +'&stu_id='+ select_data.stu_id+'&year='+select_data.year, '_blank');
}
