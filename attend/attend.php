<?php
  // todo; this should really be based on chapter
  // Although it looks like airtable doesn't care about timezones?
  date_default_timezone_set('America/Los_Angeles');

  session_start();
  require_once ('/Users/lmz/Sites/dxe/google-api-php-client/src/Google/autoload.php');

  /************************************************
    ATTENTION: Fill in these values! Make sure
    the redirect URI is to this page, e.g:
    http://localhost:8080/user-example.php
   ************************************************/
  require_once('../config/googleCredentials.php');
  $redirect_uri  = 'http://lmzdxetech.com/attend.php';

  $client = new Google_Client();
  $client->setClientId($client_id);
  $client->setClientSecret($client_secret);
  $client->setRedirectUri($redirect_uri);
  $client->setScopes('email');
  $client->addScope(Google_Service_Directory::ADMIN_DIRECTORY_GROUP_MEMBER_READONLY);

  /************************************************
    Service user authentication
    Service user is necessary for figuring out group membership
   ************************************************/
  try {
    if (strpos($service_client_id, "googleusercontent") == false
        || !strlen($service_account_name)
        || !strlen($service_key_file_location)) {
      echo missingServiceAccountDetailsWarning();
      exit;
    }
    
    $service_client = new Google_Client();
    $service_client->setApplicationName("DxE Attendance");
    $book_service = new Google_Service_Books($service_client);
    $directory_service = new Google_Service_Directory($service_client);
    
    /************************************************
      If we have an access token, we can carry on.
      Otherwise, we'll get one with the help of an
      assertion credential. In other examples the list
      of scopes was managed by the Client, but here
      we have to list them manually. We also supply
      the service account
     ************************************************/
    if (isset($_SESSION['service_token'])) {
      $service_client->setAccessToken($_SESSION['service_token']);
    }
    $service_key = file_get_contents($service_key_file_location);
    $service_cred = new Google_Auth_AssertionCredentials(
        $service_account_name,
        array(Google_Service_Directory::ADMIN_DIRECTORY_GROUP_MEMBER_READONLY),
        $service_key
    );
    // impersonate a super admin
    $service_cred->sub = $superadmin;

    $service_client->setAssertionCredentials($service_cred);
    if ($service_client->getAuth()->isAccessTokenExpired()) {
      $service_client->getAuth()->refreshTokenWithAssertion($service_cred);
    }
    $_SESSION['service_token'] = $service_client->getAccessToken();
    error_log("service_client AOK");

  } catch (Exception $e) {
    error_log('Caught service_client exception: ' . $e->getMessage());
  }

  /************************************************
    If we're logging out we just need to clear our
    local access token in this case
   ************************************************/
  if (isset($_REQUEST['logout'])) {
    unset($_SESSION['access_token']);
  }

  /************************************************
    If we have a code back from the OAuth 2.0 flow,
    we need to exchange that with the authenticate()
    function. We store the resultant access token
    bundle in the session, and redirect to ourself.
   ************************************************/
  if (isset($_GET['code'])) {
    $client->authenticate($_GET['code']);
    $_SESSION['access_token'] = $client->getAccessToken();
    $redirect = 'http://' . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'];
    header('Location: ' . filter_var($redirect, FILTER_SANITIZE_URL));
  }

  /************************************************
    If we have an access token, we can make
    requests, else we generate an authentication URL.
   ************************************************/
  if (isset($_SESSION['access_token']) && $_SESSION['access_token']) {
    $client->setAccessToken($_SESSION['access_token']);
  } else {
    $authUrl = $client->createAuthUrl();
  }

  /************************************************
    If we're signed in we can go ahead and retrieve
    the ID token, which is part of the bundle of
    data that is exchange in the authenticate step
    - we only need to do a network call if we have
    to retrieve the Google certificate to verify it,
    and that can be cached.
   ************************************************/
  try {
    if ($client->getAccessToken()) {
      $_SESSION['access_token'] = $client->getAccessToken();
      $token_data = $client->verifyIdToken()->getAttributes();

      // Is logged in user part of the given group?
      // This will throw an exception if not
      $response = $directory_service->members->get($attendance_group_key, 
                                                   $token_data['payload']['sub']);
      // For good measure though...
      assert(($response->{'role'} == 'OWNER') || ($response->{'role'} == 'MANAGER') || ($response->{'role'} == 'MEMBER'));
      assert($response->{'type'} == 'USER');
      // echo "<pre>" . print_r($response, true) . "</pre>";
    }
  } catch (Exception $e) {
    error_log('Caught exception: ' . $e->getMessage());
    error_log(print_r($token_data, True));
    $token_data = NULL;
    $authUrl = $client->createAuthUrl();
  } 

  echo get_page_header("DxE Attendance");
  if (strpos($client_id, "googleusercontent") == false) {
    echo missingClientSecretsWarning();
    exit;
  }

  print '<div class="box">';
  
  if (!isset($token_data) || isset($authUrl)) {
    print "<div class='request'><a class='login' href='" . $authUrl . "'>Login</a></div>";
    print "</div>\n"; // box 
    print get_page_footer();
    exit;
  } else {
    print '<div class="request">';
    print 'Welcome, ' . $token_data['payload']['email'] . '!   ';
    echo "<a class='logout' href='?logout'>Logout</a>";
    print '</div>';
  }
  print '</div>'; // box

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

  /* Return string for page header.
   */
  function get_page_header($title) {
    $header = '<!DOCTYPE html>
<html>
<head>
<title>' . $title . '</title>
<script src="jquery-1.11.3.min.js"></script>
<script src="jquery-ui-1.11.3.min.js"></script>
<script src="jquery-dateFormat.min.js"></script>
<link rel="stylesheet" type="text/css" href="jquery-ui-1.11.3.min.css">
<link rel="stylesheet" type="text/css" href="attend.css">
</head>
<body>
';
    return $header;
  }
  
  function get_page_footer() {
    return '</body></html>';
  }

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

  echo get_page_footer();
?>

