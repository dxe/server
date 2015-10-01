<?php
  // todo; this should really be based on chapter
  date_default_timezone_set('America/Los_Angeles');

  // todo: google login verification


  require_once('../config/airtableCredentials.php');
  $airtable_url = "https://api.airtable.com/v0/" . $AIRTABLE_BASE_ID;
  $airtable_ch  = NULL;

  /* Create a record in the given table with the given fields.
   * Returns the id on success; or null on failure.
   */
  function create_record($table, $fields) {
    global $airtable_cache, $airtable_ch, $airtable_url, $AIRTABLE_API_KEY;

    // otherwise, setup curl
    if (is_null($airtable_ch)) {
      $airtable_ch = curl_init();
      curl_setopt($airtable_ch, CURLOPT_RETURNTRANSFER, 1);
      curl_setopt($airtable_ch, CURLOPT_POST, True);
      curl_setopt($airtable_ch, CURLOPT_HTTPHEADER, array(
	"Authorization: Bearer " . $AIRTABLE_API_KEY, 
        "Content-type: application/json"));
    }
    error_log("Create record with table = " . $table);
    error_log(json_encode($fields));
    $uri = "/" . rawurlencode($table);

    curl_setopt($airtable_ch, CURLOPT_URL, $airtable_url . $uri);
    curl_setopt($airtable_ch, CURLOPT_POSTFIELDS, json_encode($fields)); 
    $return_json = curl_exec($airtable_ch);
    if (curl_errno($airtable_ch)) {
       error_log("Error: " . curl_error($airtable_ch)); 
       print "An error occurred.";
       return null;
    }  
    $return_data = json_decode($return_json);
    error_log(print_r($return_json, true));
    return $return_data->{"id"};
  }

  // on submit
  if (array_key_exists("attend", $_POST) && count($_POST["attend"]) > 0) {
    $posted = json_decode($_POST["attend"]);

    // Step 1: Add the new members to AirTable
    foreach ($posted->{"new_members"} as $id => $name) {
      error_log($id . " => [" + $name + "]");

      // remove them from attendees
      unset($posted->{"attendees"}->{$id});

      // split up name into First and Last (crudely) 
      $names = split(" ", $name, 2);
      if (count($names) == 0) { continue; }
      // populate the fields to send to airtable for the new member
      $fields = array();
      $fields["first_name"]   = $names[0];
      if (count($names) > 1) { 
        $fields["last_name"]  = $names[1]; 
      }
      $fields["member_since"] = date("Y-m-d"); 
      $fields["chapter_id"]   = array($posted->{"chapter_id"});
      $fields["notes"]        = "Added by attendance app for event " . $posted->{"event_name"};
      $new_id = create_record("All Members", array( "fields" => $fields));

      // add the new id into the record
      if (!is_null($new_id)) {
        print "<li>Added '" . $name . "' to All Members table.</li>\n";
        $posted->{"attendees"}->{$new_id} = $name;
      }
    }
    // Step 2. Add the event
    $fields              = array();
    $fields["Name"]      = $posted->{"event_name"};
    $fields["Chapter"]   = array($posted->{"chapter_id"});
    $fields["Attendees"] = array_keys(get_object_vars($posted->{"attendees"}));
    $fields["Date"]      = date("c"); // ISO 8601 date. e.g. "2004-02-12T15:19:21+00:00"
    $event_id = create_record("Events", array( "fields" => $fields));
    if (!is_null($event_id)) {
       print "<li>Added event '" . $posted->{"event_name"} . "' with " . count($fields["Attendees"]) . " attendees.</li>\n";
    }
    
    if (!is_null($airtable_ch)) { curl_close($airtable_ch); }
    return;
  }
?>

<!DOCTYPE html>
<html>
<head>
<script src="jquery-1.11.3.min.js"></script>
<script src="jquery-ui-1.11.3.min.js"></script>
<script src="jquery-dateFormat.min.js"></script>
<link rel="stylesheet" type="text/css" href="jquery-ui-1.11.3.min.css">
<link rel="stylesheet" type="text/css" href="attend.css">
</head>
<body>


<?php
  // todo: move this file to a place not accessible on the server
  $airtable_cache_str = file_get_contents("members.json");
  $airtable_cache = json_decode($airtable_cache_str, true);

  /* function that returns all the records in the given view of the given table
   * Checks the airtable on-disk cahce first and returns from there if possible
   * Otherwise performs the query to airtable and returns the result
   */
  function get_all_records($table, $view) {
    global $airtable_cache, $airtable_ch, $airtable_url, $AIRTABLE_API_KEY;

    // check cache and return from there if possible
    if (!is_null($airtable_cache) && array_key_exists($table . ":" . $view, $airtable_cache)) {
      error_log("returning cached [" . $table . ":" . $view . "]");
      return $airtable_cache[$table . ":" . $view];
    }

    // otherwise, setup curl
    if (is_null($airtable_ch)) {
      $airtable_ch = curl_init();
      curl_setopt($airtable_ch, CURLOPT_RETURNTRANSFER, 1);
      curl_setopt($airtable_ch, CURLOPT_HTTPHEADER, array("Authorization: Bearer " . $AIRTABLE_API_KEY));
    }

    $offset         = "";
    $return_records = array();

    while ($offset !== null) {

      $uri = "/" . rawurlencode($table) . "?view=" . rawurlencode($view);
      if (strlen($offset) > 0) { $uri .= "&offset=" . $offset; }
      curl_setopt($airtable_ch, CURLOPT_URL, $airtable_url . $uri);

      $return_json = curl_exec($airtable_ch);
      if (curl_errno($airtable_ch)) {
         error_log("Error: " . curl_error($airtable_ch)); 
         print "An error occurred.";
         return null;
      }  
      $return_data = json_decode($return_json);
      $offset = $return_data->offset;
      $return_records = array_merge($return_records, $return_data->records);
    }
    //error_log($return_json);
    return $return_records;
  }
?>

<h1>DxE Event Attendance App</h1>

<h2>Select your chapter</h2>

<form id="form_attend" action="attend.php">
  <?php
    $chapters = get_all_records('Chapters','Main View');
    if ($chapters !== null) {
      // pass to javascript
      print "<script type=\"text/javascript\">\n";
      print "var chapters = " . json_encode($chapters) . ";\n";
      print "</script>\n";
  
      // Create chapter select widget 
      print '<select id="select_chapter" name="select_chapter">';
      for ($chapter_index = 0; $chapter_index < count($chapters); $chapter_index++) {
         print "<pre>";
         print_r($chapters[$chapter_index]);
         print "</pre> <hr />";
         print "<option value=\"";
         if (is_array($chapters[$chapter_index])) {
           print $chapters[$chapter_index]["id"];
         } else {
           print $chapters[$chapter_index]->id;
         }
         print "\"> ";
         if (is_array($chapters[$chapter_index])) {
           print $chapters[$chapter_index]["fields"]['Name'];
         } else {
           print $chapters[$chapter_index]->fields->{'Name'};
         } 
         print "</option>\n";
      }
      print "</select>\n";
    }
  
    // all members
    $members = get_all_records('All Members', 'Main View');
    if ($members !== null) {
      // pass to javascript
      print "<script type=\"text/javascript\">\n";
      print "var members = " . json_encode($members) . ";\n";
      print "</script>\n";
    }
  ?>
  
  <h2>Name your event</h2>
  
  <div class="ui-widget">
    <label for="input_event">Event Name:</label>
    <input id="input_event" type="text">
  </div>
  
  <h2>Who is here?</h2>
  
  <div class="ui-widget">
    <label for="input_peeps">Name:</label>
    <input id="input_peeps" type="text">
  </div>
  <br />
  
  <div id="add_error" style="color:red; padding:10px" hidden=true></div>

  <button id="submit_button">Submit to Airtable DB</button>

  <div id="progressbar" hidden=true></div>
  <div id="result_div" hidden=true><ul id="result_ul"></ul></div>

  <div><ul id="peep_list"></ul></div>

</form>

<script src="attend.js"></script>
<script type="text/javascript">
// initialize the progress bar 
$( "#progressbar" ).progressbar({ value: false });
// initialize the button (disabled) while no attendees exist
$( "#submit_button" ).button({ disabled: true });
// select the first one
chapterSelected("<?php if (is_array($chapters[0])) { print($chapters[0]['id']); } else { print($chapters[0]->{'id'}); } ?>");
</script>

<?php
  // close cURL resource, and free up system resources
  if (!is_null($airtable_ch)) { curl_close($airtable_ch); }
?>
</body>
</html>

