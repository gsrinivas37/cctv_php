<?php
include ('conn.php');
include ('queries.php');

// Change below two lines to test query
$cols = array("Hour", "PersonCount", "TotalCount", "cachedir", "time");
$values = runQueryWithTwoArg($get_photos_query,"Gate", "2020-12-28", $cols);
?>

<!DOCTYPE html>
<html>
<head>

 <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
        }
        th, td {
            padding: 5px;
            text-align: left;
        }
    </style>

</head>
<body>
		<table>
			<tr>
<?php
    foreach($cols as $k => $v) {
	echo "<th><h2>$v</th>\n";		
    }?>
			</tr>
     
    <?php
    foreach($values as $k1 => $v1) {
	echo "<tr>\n";
	foreach($v1 as $k2 => $v2) {
	    echo "<td><h3>$v2</td>\n";
	}
	echo "</tr>\n";
    }
?>
   
	</table>
</body>
</html>

