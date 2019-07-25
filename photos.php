<?php
require 'vars.php';
require_once('authorize.php');
$CAMERA = $_GET["camera"];
$DATE = $_GET["date"];
$photo_dir = $CAMERA=="Gate"? $GATE_PHOTO_DIR : $STAIRS_PHOTO_DIR;
$date_dirs = array_filter(glob($photo_dir."/$DATE/*"), 'is_dir');
arsort($date_dirs);
?>


<html>
<title><?php echo "$CAMERA Photos ($DATE)"?></title>
<head><h1><center><a href='./index.php'><?php echo $CAMERA ?>Photos</a> <?php echo "($DATE)"?> </a></center></h1>
    <style>
        div.gallery {
            margin: 5px;
            border: 2px solid #ccc;
            float: left;
            width: 300px;
        }

        div.gallery:hover {
            border: 2px solid #777;
        }

        div.gallery img {
            width: 100%;
            height: auto;
        }

        div.desc {
            font-size: larger;
            font-weight: bolder;
            padding: 10px;
            text-align: center;
            background-color: #5DADE2;
        }
    </style>
</head>

<body>

<?php
$today = strtotime($DATE);
$yday = date('Y-m-d', strtotime('-1 day', $today ));
$tmrw = date('Y-m-d', strtotime('1 day', $today));
echo '<h2>';
if(file_exists("$photo_dir/$yday")){
    echo "<div style='float: left'><a href='./photos.php?camera=$CAMERA&date=$yday'> Previous</a> ($yday)</div>\n";
}
if(file_exists("$photo_dir/$tmrw")) {
    echo "<div style='float: right'><a href='./photos.php?camera=$CAMERA&date=$tmrw'> Next</a> ($tmrw)</div>\n";
}
echo "<div style='margin: auto; width: 250px;'>&emsp;&emsp;</div></h2>\n";

foreach($date_dirs as $k => $v){
    $hour = basename($v);

    $p_images = getPersonImages($v);
    $o_images = getOtherImages($v);
    $all_images = array_merge($p_images,$o_images);

    $p_count = count($p_images);
    $t_count = count($all_images);

    reset($p_images);
    $img = current($p_images);
    if($p_count==0){
        reset($all_images);
        $img = current($all_images);
    }

    $cam = $CAMERA=="Gate"?"GatePhotos":"StairsPhotos";
    $img_link = "./$cam/$DATE/$hour/$img";
    $thumb_link = "./$cam/$DATE/$hour/thumbnails/$img";
    if(!file_exists("$HDD_ROOT/$cam/$DATE/$hour/thumbnails/$img")){
        $thumb_link = $img_link;
    }

    echo "<div class='gallery''>\n";
    echo "<a href='./preview.php?camera=$CAMERA&date=$DATE&hour=$hour'> <img src=$thumb_link alt='Cinque Terre' width='600' height='400'> </a>\n";
    echo "<div class='desc'>$hour ( $p_count / $t_count ) </div>\n";
    echo "</div>\n";
}
?>

</body>
</html>