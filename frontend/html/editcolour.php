


<!DOCTYPE html>

<html>
<head>
    <meta charset="UTF-8">
    <title>UMD Manager Edit Colours</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="bower_components/bootstrap/dist/css/bootstrap.min.css">
    <script src="base.js"></script>
    <link href = "bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css" rel="stylesheet">
    <!-- Select -->
    <link href = "bower_components/bootstrap-select/dist/css/bootstrap-select.css" rel="stylesheet">
    <!-- Custom styles for this template -->

    <link href="bower_components/bootstrap-combobox/css/bootstrap-combobox.css" rel="stylesheet"/>
    <!-- Required Javascript -->
    <script src="bower_components/jquery/dist/jquery.min.js"></script>
    <script src="bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
    <script src="bower_components/bootstrap-treeview/src/js/bootstrap-treeview.js"></script>
    <script src="bower_components/progressbar.js/dist/progressbar.min.js"></script>
    <script src="bower_components/d3/d3.js"></script>
    <script src="bower_components/moment/moment.js"></script>
    <script src="bower_components/moment-timezone/builds/moment-timezone-with-data.js"></script>
    <script src="bower_components/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js"></script>
    <script src="bower_components/bootstrap-select/dist/js/bootstrap-select.js"></script>
    <script src="bower_components/bootstrap-combobox/js/bootstrap-combobox.js"></script>
    <script src="bower_components/bootstrap-toggle/js/bootstrap-toggle.js"></script>
    <script src="bower_components/bootstrap-table/dist/bootstrap-table.js"></script>
    <script src="node_modules/@json-editor/json-editor/dist/jsoneditor.min.js"></script>
</head>

<body>

<ul class="nav nav-tabs" role="tablist">
    <li ><a href="editmv.html">Multiviewer</a></li>
    <li><a href="editird.html">IRD</a></li>
    <li class="active"><a href="editcolour.php">Colours</a></li>
</ul>


<div class="page-header">
    <h2>Eurovision UMD Manager
        <small>Edit Colours</small>
    </h2>
</div>


<?php
error_reporting(E_ALL);
ini_set( 'display_errors','1');

require_once ('sql.php');
dbstart();
if(isset($_GET['mode'])) {
    $mode = $_GET['mode'];
}
$ressource = select_db("umd");

if ($_SERVER['REQUEST_METHOD']=="POST") {
    echo "<tr><td>";
    echo implode("</td><td>", $_POST);
    echo "</td></tr>";
    global $conn;
    if (isset($_POST['id'])) {
        if ($_POST['action'] == "remove"){
            $id = $_POST['id'];

            $stmt = $conn->prepare('delete from colours where id = ?');
            $stmt->bind_param('i', $id);
            $stmt->execute();
            $stmt->close();
            echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
              Deleted colour '.$id.'
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>';
        }else{

            $id = $_POST['id'];
            $name = $_POST['name'];
            $colour = $_POST['colour'];
            $stmt = $conn->prepare('update colours set name = ?, colour = ? where id = ?');
            $stmt->bind_param('ssi',$name, $colour, $id);
            $stmt->execute();
            $stmt->close();

            echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
              Updated colour '.$id.'
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>';
        }
    }else{



        $name = $_POST['name'];
        $colour = $_POST['colour'];
        $stmt = $conn->prepare('insert into colours set name = ?, colour = ?');
        $stmt->bind_param('ss',$name, $colour);
        $stmt->execute();
        $stmt->close();

        echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
              Added new colour.
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>';

    }
}



?>

<table class = "table table-responsive">
    <thead><tr>
        <td>Remove</td>
        <td>ID</td>
        <td>Name</td>
        <td>Colour</td>
        <td>Sumbit</td>
    </tr></thead>
    <tbody>
<?php
$db = select_db("UMD");
$sql = 'SELECT * FROM `colours`';
$colours = query($sql);
$num_rows=mysqli_num_rows($colours);

for($x=0; $x < $num_rows; $x++ )
{

    //echo '<form> <div class="form-row">';
    echo "<tr><form method='post' action='#'>";
    $row = mysqli_fetch_assoc($colours);

    //echo ' <div class="col">';
    echo "<td>";
    echo '<input type = "hidden" name="id" value="'.$row["id"].'">';
    echo '<input type="hidden" class="form-control" name="action" value="remove">';
    echo '<button class="btn btn-danger"  type="submit" >';
    echo '<span class="glyphicon glyphicon-remove" aria-hidden="true" ></span></button>';
    //echo "</div>";
    echo "</form></td>";
    echo "<td><form method='post' action='#'>";

    //echo ' <div class="col">';
    echo '<input type = "hidden" name="id" value="'.$row["id"].'">';
    echo '<input type="hidden" class="form-control" name="action" value="modify">';
    echo $row["id"];
    //echo "</div>";
    //echo ' <div class="col">';
    echo "</td>";
    echo "<td>";
    echo '<input type="text" class="form-control" name="name" value="'.$row["name"].'">';

    //echo "</div>";
    //echo ' <div class="col">';
    echo "</td>";
    echo "<td>";
    echo '<input type="color" class="form-control" name="colour" value="'.$row["colour"].'">';
    echo $row["colour"];
    //echo "</div>";
    echo "</td>";
    echo '<td><button type="submit"  class="btn btn-default">Submit</button></td>';
    echo "</form>";
    echo "</tr>";

}

// Free result set
mysqli_free_result($colours);

dbend();
?>



<tr><form method='post' action='#'>
        <td>
        </td>
        <td>
        <td>
            <input type="hidden" class="form-control" name="action" value="add">
            <input type="text" class="form-control" name="name" placeholder="Identifier">
        </td>
        <td>
            <input type="color" class="form-control" name="colour" value="#00ffaa">
            </div>
        </td>
        <td><button type="submit"  class="btn btn-default">Add</button></td>
    </form>
</tr>
    </tbody>
</table>
</body>
</html>