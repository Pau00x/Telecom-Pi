<?php

session_start();
// Variables globals
$host = "localhost";
$user = "root";
$password = "agrfs910.";
$db = "PBE";


// Determinem quina funció s'ha de fer segons la taula
switch(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH)){
	case "/students":
		login();
		break;
	case "/tasks":
		dbsearch();
		break;
	case "/timetables":
		dbsearch();
		break;
	case "/marks":
		dbsearch();
		break;
	case "/logout":
		logout();
		break;
	default:
		echo "Invalid petition";
}

// Funció que inicia sessió (Troba el nom de l'usuari)
function login(){
	global $host, $user, $password, $db;
	
	// Connexió amb l base de dades
	$conn = mysqli_connect($host, $user, $password, $db);
	
	// Retorna error si no es pot realitzar la connexió amb la base de dades
	if (mysqli_connect_errno()) {
		printf("Failed to connect %s\n", mysqli_connect_error());
		exit();
	}
  
	// Obtenim la variable QUERY_STRING actual i separem per variables
	$str = $_SERVER['QUERY_STRING'];
	parse_str($str);
  
	// Enviem la query a la base de dades
	$result = mysqli_query($conn, "SELECT name FROM students WHERE student_id = '$student_id'");
	
	// Emmagatzemem el resultat de la consulta en un array
	$rows = array();
	while($r = mysqli_fetch_assoc($result)) {
		$rows[] = $r;
	}
	
	// Retornem l'array en format json
	echo json_encode($rows);
	
	mysqli_close($conn);
	
	//Comprovem que l'usuari està a la base de dades i iniciem un comptador
	if(count($rows) == 1){
		$_SESSION['LAST_ACTIVITY'] = time(); // update last activity time stamp
	}
	
	//En cas de no ser-hi destruim la sessió actual
	else{
		sleep(1);
		session_unset();
		sleep(1);
		session_destroy(); 
		return;
	}
}

// Funció que fa la consulta de la query
function dbsearch(){
	global $host, $user, $password, $db;
	
	if (isset($_SESSION['LAST_ACTIVITY']) && (time() - $_SESSION['LAST_ACTIVITY'] > 20)) {
    // last request was more than 20 seconds ago
    echo "Not logged in";
    session_unset();     // unset $_SESSION variable for the run-time 
    session_destroy();   // destroy session data in storage
    return;
	}
	$_SESSION['LAST_ACTIVITY'] = time(); // update last activity time stamp
	
	$conn = mysqli_connect($host, $user, $password, $db);

	// Obtenim la taula on farem la consulta
	$table = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
	$table = preg_replace("/[^a-zA-Z0-9\s]/", "", $table);

	// Retorna error si no es pot realitzar la connexió amb la base de dades
	if (mysqli_connect_errno()) {
		printf("Failed to connect %s\n", mysqli_connect_error());
		exit();
	}
	
	// Iniciem la sentència de la query
	$query = "SELECT * FROM $table ";
	
	// Creem un array on emmagatzemem parelles de dades (clau, valor)
	$carray = array();
	$str = $_SERVER['QUERY_STRING'];
	parse_str($str, $carray);

	// Recorrem l'array i afegim les constraints a la query
	$i = 0;
	foreach($carray as $constr=>$cvalue){
		switch($constr){
			case "limit":
				$query .= "$constr $cvalue ";
				break;
		default:
			if($i!=0){
				$query .= "and ";
			} else {
				$query .= "WHERE ";
			}
			$i++;
			$query .= "$constr = '$cvalue' ";
		}
	}

	// Enviem la query a la base de dades
	$result = mysqli_query($conn, $query);
	
	// Emmagatzemem el resultat de la consulta en un array
	$rows = array();
	while($r = mysqli_fetch_assoc($result)) {
		$rows[] = $r;
	}
 
	// Retornem l'array en format json
	echo json_encode($rows);
	
	mysqli_close($conn);
}

function logout(){
	session_unset();
	session_destroy(); 
}

?>
