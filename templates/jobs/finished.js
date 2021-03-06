<!-- page script -->
<script>
$(function () {
  var table = $("#jobsfinished").DataTable({
    "serverSide": true,
    "ajax": "{% url 'jobsfinisheddata' %}",
    "language": {
      "emptyTable": "No Jobs finished"
    },
    "order": [[ 0, 'desc' ]],
    "bAutoWidth": false,
    "columns": [
      { "width": "30px", "sClass": "vertical-align text-center" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderjoblink(data)} },
      { "sClass": "vertical-align", "render": function (data,type,row){ return renderclientlink(data)} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align" },
      { "width": "50px", "sClass": "vertical-align text-center", "render": function (data,type,row){ return renderlevelbadge(data[0],data[1])} },
      { "sClass": "vertical-align" },
      { "sClass": "vertical-align", "render": function (data,type,row){ return bytestext(data)} },
      { "width": "96px", "orderable": false, "sClass": "vertical-align text-center", <!-- 32px for every button -->
        "render": function (data,type,row){
          var btn = '<button class="btn btn-sm btn-default" type="button" ';
          var blog = btn + 'onclick="location.href=\'{% url 'jobslog_rel' %}'+data[0]+'/\';"><i class="fa fa-info-circle" data-toggle="tooltip" data-original-title="Information"></i></button>\n';
          var bres = btn + 'onclick="location.href=\'{% url 'restorejobid_rel' %}'+data[0]+'/\';"><i class="fa fa-cloud-upload" data-toggle="tooltip" data-original-title="Restore"></i></button>\n';
          var bdel = btn + 'data-toggle="modal" data-target="#deletejobidconfirm" data-name="'+data[1]+'" data-jobid="'+data[0]+'" data-url="{% url 'jobsiddelete_rel' %}"><i class="fa fa-trash" data-toggle="tooltip" data-original-title="Delete"></i></button>\n';
          var ret = '<div class="btn-group">' + blog + bdel + '</div>';
          if (data[2] == 'B'){
            ret = '<div class="btn-group">' + blog + bres + bdel + '</div>';
          };
          return ret;
        },
      },
    ],
  });
  setInterval( function () {
    table.ajax.reload( null, false ); // user paging is not reset on reload
  }, 60000 );
{% include "widgets/refreshbutton.js" %}
{% include "widgets/confirmbutton.js" with selector='#deletejobidconfirmbutton' %}
});
{% include "widgets/confirmmodal2.js" with selector='#deletejobidconfirm' %}
{% include "widgets/renderlinks.js" %}
</script>
{% include "pages/refresh.js" with jobstatuswidgetRefresh=1 %}
{% include 'widgets/helpbutton.js' with helppage='jobs.finished' %}