
// global
var name_to_id = {};
var attendees  = {};  // id -> full name
var new_members= {};  // id -> full name
// console.log("members:");
// console.log(members[0]);

$("#select_chapter").on('change', function() {
  chapterSelected(this.value);
});

/* select chapter -- load relevent events into the event selector
 * or show link to event create page if none exist
 */
function chapterSelected(chapter_id) {
  console.log("chapterSelected(" + chapter_id + ") called");

  // put members for this chapter into the event list
  var container = $("#chapter_peeps");
  name_to_id = {};
  container.empty(); 
  for (var index=0; index < members.length; ++index) {
    // console.log(members[index].fields['chapter_id']);
    if ($.inArray(chapter_id, members[index].fields['chapter_id']) >= 0) {

      var fullname = members[index].fields['first_name'];
      if (typeof fullname === 'undefined') {
        fullname = "";
      } else {
        fullname += " ";
      }
      if (typeof members[index].fields['last_name'] !== 'undefined') {
        fullname += members[index].fields['last_name'];
      }
      // console.log("fullname = [" + fullname + "]");
      if (fullname.length === 0) { continue; }
      name_to_id[fullname] = members[index].id;
    }
  }
  // console.log(name_to_id);
  $("#input_peeps").autocomplete({ source:Object.keys(name_to_id),
                                   select:function(event,ui) { enter_peep(); return false; }
                                  });
}

/* On enter in the person input:
 * - if they've already been entered, error
 * - lookup their ID
 * - add them to the var list(s)
 * - add them to the DOM list
 */
$('#input_peeps').bind("enterKey",function(event){
  enter_peep();
});

function enter_peep() {
  var fullname = $( "#input_peeps" ).val();
  // it's only whitespace
  if (/^\s*$/.test(fullname)) { return; }
  console.log("inputted [" + fullname + "]");
 
  // clear the widget
  $( "#input_peeps ").val('');

  // create a unique id
  var id = fullname.replace(/ /g,"_");
  if (fullname in name_to_id) { id = name_to_id[fullname]; }
  else { new_members[id] = fullname; }

  // if they're already in the list -- error
  if (id in attendees) {
    $("#add_error").html("'" + fullname + "' is already an attendee");
    $("#add_error").show();
    return;
  }

  // add them to my list
  attendees[id] = fullname;

  // add them to the DOM list
  var elem = '<li id="' + id + '">';
  elem += '<span style="display:inline-block; width:300px">' + fullname + '</span>';
  elem += '<button id="del_' + id + '" type="button"></button>';
  elem += '</li>';
  $("#peep_list").append(elem);

  $("#del_" + id).button({ icons:{primary:"ui-icon-closethick"}, text:false });
  $("#del_" + id).on("click", function (event) {
    var remove_id = $(event.target).parents('li').attr('id');
    // console.log("button clicked remove id = [" + remove_id + "]");
    $("#" + remove_id).remove();
    delete attendees[remove_id];
  });

  // enable submit button
  $( "#submit_button").button( "option", "disabled", false );
 
}

/* On enter in the event input:
 * - shift focus to the person input
 */
$('#input_event').keydown(function(event){
  if(event.keyCode == 13) { 
    $("#input_peeps").focus();
    event.preventDefault();
    return false;
  }
});

// triger enterKey above when enter is pressed into peeps input field
$('#input_peeps').keydown(function(event){
  // console.log("keyup with key = " + e.keyCode);
  if(event.keyCode == 13) { 
    $(this).trigger("enterKey"); 
    event.preventDefault();
    return false;
  }
  else { $("#add_error").hide(); }

});


// don't submit the form
$( "form" ).submit(function( event ) {
  event.preventDefault();
  
  var form_data = {};
  form_data.chapter_id 	= $("#select_chapter").val();
  form_data.event_name 	= $("#input_event").val();
  form_data.attendees  	= attendees;
  form_data.new_members	= new_members;
   
  // console.log("form data = ");
  // console.log(form_data);

  // disable the submit button
  $( "#submit_button" ).button( "option", "disabled", true );
  // start progress bar
  $( "#progressbar" ).progressbar({ value: false });
  $( "#progressbar").show();

  $.ajax({
    type:    'POST',
    url:     $("#form_attend").attr("action"),
    data:    {'attend': JSON.stringify(form_data)},
    success: function(data) {
       console.log("response: "+data);
       $( "#progressbar").hide();
       $("#result_ul").append(data);
       $("#result_div").show();
    }});
});
