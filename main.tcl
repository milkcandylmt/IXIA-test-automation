#coding=utf-8
proc create_xml_tree {model} {
    # set f [open c:/loglmt.txt a]
    # puts $f $model
	# close $f
	package require tdom
	source "cases/$model.tcl"
	#global dtm
	set doc [dom createDocument "model"]  ;# ????xml??dom????
	set doc_root [$doc documentElement]
	$doc_root setAttribute "name" "$model"
	foreach id [lsort -integer [array names dtm -regexp {^\d+$}]] {
		eval $dtm($id)
		set casename $dtm($id,name)
		$doc_root appendChild [set doc_mod [$doc createElement "case"]]
		$doc_mod setAttribute "id" $id
		set idp $id
		append idp _
		set casename [append idp $casename]
		$doc_mod setAttribute "name" $casename
		#puts $casename
	}
	#puts "4444444444"
	set fid [open "cases/$model.xml" "RDWR APPEND CREAT TRUNC"]
	#set fid [open "$model.xml" w+]
	#puts $fid
	fconfigure $fid -blocking 0 -buffering full -encoding utf-8
	puts $fid {<?xml version="1.0" encoding="UTF-8"?>}
	puts $fid [$doc_root asXML -indent 2]
	flush $fid
	close $fid
}
proc getargs {id} {
	global dtm
	eval $dtm($id)
	set case_name $dtm($id,name)
	set webcfg $dtm($id,webcfg)
	set steps [string trim $dtm($id,step)]
	set steps [string map  {\n , \t \ } $steps]
	return \[\"$case_name\",\"$webcfg\",\"$steps\"]
}
proc getpos {id} {
	global dtm
	eval $dtm($id)
	set case_name $dtm($id,name)
	set repos $dtm($id,repos)
	return \[\"$case_name\",\"$repos\"]
}