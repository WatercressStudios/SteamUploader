# Tool by Sagittaeri

label main_menu:
    show screen steam_uploader_main

init python:
    import os, glob, shutil, zipfile, json, platform

    app_depotline_template = """\t\t"{depotid}"	"{vdfpath}"
"""

    app_template = """"appbuild"
{{
	"appid" "{appid}"
	"desc" "{appname}"
	"buildoutput" "{outputpath}"
	"contentroot" ""
	"setlive" ""
	"preview" "0"
	"local"	""
	"depots"
	{{
{depotlist}
	}}
}}
"""

    depot_template = """"DepotBuildConfig"
{{
	"DepotID" "{depotid}"
	"desc" "{depotname}"
	"contentroot" "{contentpath}"
	"FileMapping"
	{{
		"LocalPath" "*"
		"DepotPath" "."
		"recursive" "1"
	}}
	"FileExclusion" "*.pdb"
}}
"""

    root_dir = None
    for p in config.searchpath:
        if p.endswith('/game'):
            root_dir = p[:-5]
    root_root_dir = os.path.abspath(root_dir+'/..')

    project_list = []
    for p in os.listdir(root_root_dir):
        f = '{0}/{1}'.format(root_root_dir, p)
        if not os.path.isdir(f):
            continue
        if f.endswith('-dists'):
            for g in os.listdir(f):
                if os.path.isfile('{0}/{1}/{2}'.format(root_root_dir, p, g)) and g.endswith('-market.zip'):
                    project_list.append(p)
    project_name = "NO MARKETPLACE BUILD FOUND"
    project_dir = '{0}/{1}'.format(root_root_dir, project_name)
    project_build_file = None
    project_dlc_files = None
    project_input_editing = None
    project_app_id = ""
    project_depot_id = ""
    project_depot_id_dlc = {}
    steam_username = ""
    steam_password = ""
    uploading_message = ""
    is_running = False

    if os.path.isfile("{0}/steamuploader.config".format(root_dir)):
        config_json = json.loads(open("{0}/steamuploader.config".format(root_dir), "r").read())
        steam_username = config_json.get('username', '')
        steam_password = config_json.get('password', '')

    if os.path.isfile("{0}/steamupload/projectinfo.config".format(project_dir)):
        config_json = json.loads(open("{0}/steamupload/projectinfo.config".format(project_dir), "r").read())
        project_app_id = config_json.get('appid', '')
        project_depot_id = config_json.get('depotid', '')
        project_depot_id_dlc = config_json.get('dlc', {})

    def SteamUploader_VarUpdate():
        renpy.restart_interaction()

    def SteamUploader_LoadProject(project_to_load):
        global project_name, project_dir, root_root_dir
        global project_build_file, project_dlc_files
        global project_input_editing, project_app_id, project_depot_id, project_depot_id_dlc

        project_name = project_to_load
        project_dir = '{0}/{1}'.format(root_root_dir, project_name)
        if not os.path.isdir("{0}/steamupload".format(project_dir)):
            os.makedirs("{0}/steamupload".format(project_dir))

        i = 0
        project_dlc_files = []
        project_depot_id_dlc = {}
        for g in os.listdir(project_dir):
            f = '{0}/{1}'.format(project_dir, g)
            if os.path.isfile(f) and g.endswith('-market.zip'):
                project_build_file = g
            elif os.path.isdir(f) and g.endswith('-dlc'):
                i += 1
                project_dlc_files.append(g)
                project_depot_id_dlc[i] = ""

        if os.path.isfile("{0}/steamupload/projectinfo.config".format(project_dir)):
            config_json = json.loads(open("{0}/steamupload/projectinfo.config".format(project_dir), "r").read())
            project_app_id = config_json.get('appid', '')
            project_depot_id = config_json.get('depotid', '')
            project_depot_id_dlc = config_json.get('dlc', {})

    if len(project_list) > 0:
        SteamUploader_LoadProject(project_list[0])

    SteamUploader_VarUpdate()

    def SteamUploader_CanUpload():
        global project_input_editing, project_app_id, project_depot_id, project_depot_id_dlc, project_dlc_files

        if project_app_id == "":
            return False
        if project_depot_id == "":
            return False
        for k in project_depot_id_dlc:
            if project_depot_id_dlc[k] == "":
                return False
        return True

    def SteamUploader_Execute():
        global project_name, project_dir, root_dir, root_root_dir
        global project_build_file, project_dlc_files
        global project_app_id, project_depot_id, project_depot_id_dlc
        global app_depotline_template, app_template, depot_template
        global steam_username, steam_password, uploading_message, is_running

        if not os.path.isdir("{0}/SteamPipeContentBuilder".format(root_root_dir)):
            shutil.copytree("{0}/SteamPipeContentBuilder".format(root_dir), "{0}/SteamPipeContentBuilder".format(root_root_dir))

        build_dir = "{0}/steamupload".format(project_dir)
        scripts_dir = "{0}/steamupload/scripts".format(project_dir)
        output_dir = "{0}/steamupload/output".format(project_dir)
        content_dir = "{0}/steamupload/content".format(project_dir)
        if os.path.isdir(scripts_dir):
            shutil.rmtree(scripts_dir)
        os.makedirs(scripts_dir)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        if os.path.isdir(content_dir):
            shutil.rmtree(content_dir)
        os.makedirs(content_dir)

        app_file_depotlist = app_depotline_template.format(depotid=project_depot_id, vdfpath="{0}/depot_{1}.vdf".format(scripts_dir, project_depot_id))
        for k in project_depot_id_dlc:
            app_file_depotlist += app_depotline_template.format(depotid=project_depot_id_dlc[k], vdfpath="{0}/depot_{1}.vdf".format(scripts_dir, project_depot_id_dlc[k]))
        open("{0}/app_{1}.vdf".format(scripts_dir, project_app_id), "w").write(app_template.format(
            appid=project_app_id,
            appname=project_name,
            outputpath=output_dir,
            depotlist=app_file_depotlist)
        )

        open("{0}/depot_{1}.vdf".format(scripts_dir, project_depot_id), "w").write(depot_template.format(
            depotid=project_depot_id,
            depotname="{0} Content".format(content_dir),
            contentpath="{0}/{1}".format(content_dir, project_build_file[:-4]))
        )
        with zipfile.ZipFile("{0}/{1}".format(project_dir, project_build_file), 'r') as zipObj:
           zipObj.extractall(content_dir)

        i = 0
        for dlc in project_dlc_files:
            i += 1
            open("{0}/depot_{1}.vdf".format(scripts_dir, project_depot_id_dlc[k]), "w").write(depot_template.format(
                depotid=project_depot_id_dlc[unicode(i)],
                depotname=dlc,
                contentpath="{0}/{1}".format(content_dir, dlc))
            )
            shutil.copytree("{0}/{1}".format(project_dir, dlc), "{0}/{1}".format(content_dir, dlc))

        uploading_message = "Scripts generation done!\n\nUploading now..."
        renpy.restart_interaction()

        if platform.system() == "Windows":
            builder_path = '{0}/SteamPipeContentBuilder/builder/steamcmd.exe"'.format(root_root_dir)
            i = builder_path.index(':') + 1
            builder_path = builder_path[:i] + '"' + builder_path[i:]
            steampipe_output_path = '"{0}/steampipe_output.txt"'.format(output_dir)
            command = [builder_path, "+login", steam_username, steam_password, "+run_app_build_http", '"{0}/app_{1}.vdf"'.format(scripts_dir, project_app_id), "+quit"]
        elif platform.system() == "Darwin":
            builder_path = '"{0}/SteamPipeContentBuilder/builder_osx/steamcmd.sh"'.format(root_root_dir)
            steampipe_output_path = '"{0}/steampipe_output.txt"'.format(output_dir)
            command = ["sh", builder_path, "+login", steam_username, steam_password, "+run_app_build_http", '"{0}/app_{1}.vdf"'.format(scripts_dir, project_app_id), "+quit", "2>&1", ">", steampipe_output_path]
        else:
            builder_path = '"{0}/SteamPipeContentBuilder/builder_linux/steamcmd.sh"'.format(root_root_dir)
            steampipe_output_path = '"{0}/steampipe_output.txt"'.format(output_dir)
            command = ["sh", builder_path, "+login", steam_username, steam_password, "+run_app_build_http", '"{0}/app_{1}.vdf"'.format(scripts_dir, project_app_id), "+quit", "2>&1", ">", steampipe_output_path]

        print ' '.join(command).replace('\\', '/')
        return_code = os.system(' '.join(command).replace('\\', '/'))

        uploading_message = "Done! Return code is {0}".format(return_code)
        is_running = False
        renpy.restart_interaction()


    class SteamUploader_ChangeSelectedProject:
        def __init__(self, i):
            self.i = i
        def __call__(self):
            global project_list
            SteamUploader_LoadProject(project_list[self.i])
            SteamUploader_VarUpdate()

    class SteamUploader_ChangeCurrentEditing:
        def __init__(self, i):
            self.i = i
        def __call__(self):
            global project_input_editing
            project_input_editing = self.i
            SteamUploader_VarUpdate()

    class SteamUploader_ChangeAppID:
        def __call__(self, i):
            global project_app_id, project_depot_id, project_depot_id_dlc, project_dir
            project_app_id = i
            SteamUploader_VarUpdate()

            config_json = {}
            config_json['appid'] = project_app_id
            config_json['depotid'] = project_depot_id
            config_json['dlc'] = project_depot_id_dlc
            open("{0}/steamupload/projectinfo.config".format(project_dir), "w").write(json.dumps(config_json))

    class SteamUploader_ChangeDepotID:
        def __init__(self, dlc=None):
            self.dlc = dlc
        def __call__(self, i):
            global project_app_id, project_depot_id, project_depot_id_dlc, project_dir
            if not self.dlc is None:
                project_depot_id_dlc[self.dlc] = i
            else:
                project_depot_id = i
            SteamUploader_VarUpdate()

            config_json = {}
            config_json['appid'] = project_app_id
            config_json['depotid'] = project_depot_id
            config_json['dlc'] = project_depot_id_dlc
            open("{0}/steamupload/projectinfo.config".format(project_dir), "w").write(json.dumps(config_json))

    class SteamUploader_ChangeUsername:
        def __call__(self, i):
            global steam_username, steam_password, root_dir
            steam_username = i
            SteamUploader_VarUpdate()

            config_json = {}
            config_json['username'] = steam_username
            config_json['password'] = steam_password
            open("{0}/steamuploader.config".format(root_dir), "w").write(json.dumps(config_json))

    class SteamUploader_ChangePassword:
        def __call__(self, i):
            global steam_username, steam_password, root_dir
            steam_password = i
            SteamUploader_VarUpdate()

            config_json = {}
            config_json['username'] = steam_username
            config_json['password'] = steam_password
            open("{0}/steamuploader.config".format(root_dir), "w").write(json.dumps(config_json))

    class SteamUploader_DoUpload:
        def __call__(self):
            global steam_username, steam_password, uploading_message, is_running

            if steam_username == "" or steam_password == "":
                return

            uploading_message = "Generating files...\n\nPlease wait..."
            is_running = True
            renpy.show_screen("steam_upload_uploading")
            renpy.restart_interaction()

screen steam_uploader_main:
    fixed:
        xysize (1.0, 1.0)
        label "{b}>> STEAM UPLOADER TOOL <<{/b}":
            align (0.5, 0.03)

        frame:
            xysize (0.9, 0.9)
            align (0.5, 0.5)
            padding (80, 40)
            vbox:
                spacing 5
                hbox:
                    spacing 30
                    label "Choose build:" ysize 40 text_yalign 0.5
                    button:
                        background Solid("222")
                        hover_background Solid("225e")
                        xysize (400, 40)
                        margin (0,0)
                        padding (0,0)
                        action ToggleScreen("steam_uploader_dropdown",
                            currentselected=project_name,
                            selectionlist=project_list,
                            callback=SteamUploader_ChangeSelectedProject,
                            offset=(-60, 20))
                        text project_name:
                            size 20
                            color "fff"
                            align (0.5, 0.5)
                            text_align 0.5
                if not project_build_file is None:
                    null height 30
                    label "{b}>> PACKAGE INFO <<{/b}"
                    null height 10
                    hbox:
                        spacing 30
                        fixed:
                            xysize (200, 30)
                            label "Main content:" xalign 1.0
                        label project_build_file
                    hbox:
                        spacing 30
                        fixed:
                            xysize (200, 30)
                            text "App ID:" xalign 1.0
                        if project_input_editing == "appid":
                            input:
                                default project_app_id
                                allow "0123456789"
                                length 12
                                copypaste True
                                changed SteamUploader_ChangeAppID()
                        else:
                            textbutton project_app_id:
                                xysize (200, 30)
                                action SteamUploader_ChangeCurrentEditing("appid")
                    hbox:
                        spacing 30
                        fixed:
                            xysize (200, 30)
                            text "Depot ID:" xalign 1.0
                        if project_input_editing == "depotid":
                            input:
                                default project_depot_id
                                allow "0123456789"
                                length 12
                                copypaste True
                                changed SteamUploader_ChangeDepotID()
                        else:
                            textbutton project_depot_id:
                                xysize (200, 30)
                                action SteamUploader_ChangeCurrentEditing("depotid")
                    if len(project_dlc_files) == 0:
                        null height 20
                        label "No DLC package found" xalign 0.5
                        null height 10
                        label "NOTE: DLC folders should end with '-dlc' and\nbe in the same folder as the '-market.zip' file" xalign 0.5
                    else:
                        $ i = 0
                        for dlc in project_dlc_files:
                            $ i += 1
                            null height 20
                            hbox:
                                spacing 30
                                fixed:
                                    xysize (200, 30)
                                    label "DLC " + str(i) + ":" xalign 1.0
                                label dlc
                            hbox:
                                spacing 30
                                fixed:
                                    xysize (200, 30)
                                    text "Depot ID:" xalign 1.0
                                if project_input_editing == "depotid_dlc_"+str(i):
                                    input:
                                        default project_depot_id_dlc.get(unicode(i), "")
                                        allow "0123456789"
                                        length 12
                                        copypaste True
                                        changed SteamUploader_ChangeDepotID(i)
                                else:
                                    textbutton project_depot_id_dlc.get(unicode(i), ""):
                                        xysize (200, 30)
                                        action SteamUploader_ChangeCurrentEditing("depotid_dlc_"+str(i))

        if SteamUploader_CanUpload():
            hbox:
                align (0.5, 0.9)
                spacing 5
                fixed:
                    xysize (120, 35)
                    text "Username:" align (1.0, 0.5)
                if project_input_editing == "username":
                    frame:
                        xysize (200, 35)
                        input:
                            default steam_username
                            length 12
                            copypaste True
                            changed SteamUploader_ChangeUsername()
                else:
                    frame:
                        xysize (200, 35)
                        textbutton steam_username:
                            xysize (190, 35)
                            align (0.5, 0.5)
                            action SteamUploader_ChangeCurrentEditing("username")
                fixed:
                    xysize (120, 35)
                    text "Password:" align (1.0, 0.5)
                if project_input_editing == "password":
                    frame:
                        xysize (200, 35)
                        input:
                            default steam_password
                            length 12
                            copypaste True
                            changed SteamUploader_ChangePassword()
                else:
                    frame:
                        xysize (200, 35)
                        textbutton steam_password:
                            xysize (190, 35)
                            align (0.5, 0.5)
                            action SteamUploader_ChangeCurrentEditing("password")

                null width 30
                button:
                    background Solid("222")
                    hover_background Solid("225e")
                    xysize (250, 50)
                    margin (0,0)
                    padding (0,0)
                    yoffset -10
                    action [ SteamUploader_DoUpload() ]
                    text "UPLOAD":
                        size 20
                        color "fff"
                        align (0.5, 0.5)
                        text_align 0.5

screen steam_uploader_dropdown(currentselected, selectionlist, callback, offset=(0,0)):
    zorder 201
    frame:
        background None
        xysize (1.0, 1.0)
        margin (0,0)
        padding (0,0)
        button:
            background Solid("222e")
            align (0.94, 0.3)
            offset offset
            xysize (400, 600)
            margin (0,0)
            padding (15,15,50,15)
            action Hide("steam_uploader_dropdown")
            viewport id "steam_uploader_viewport_dropdown":
                draggable True
                mousewheel True
                vbox:
                    spacing 5
                    for i in range(len(selectionlist)):
                        $ t = selectionlist[i]
                        if t == currentselected:
                            $ t = '{b}'+t+'{/b}'
                        button:
                            background Solid("000e")
                            hover_background Solid("225e")
                            xsize 1.0
                            action [ callback(i),
                                    Show('steam_uploader_main'),
                                    Show('steam_uploader_dropdown',
                                        currentselected = selectionlist[i],
                                        selectionlist = selectionlist,
                                        callback = callback,
                                        offset = offset),
                                        Hide("steam_uploader_dropdown") ]
                            text t:
                                size 20
                                color "fff"
                                xalign 0.5
                                text_align 0.5
            vbar value YScrollValue("steam_uploader_viewport_dropdown"):
                xalign 1.0
                xoffset 35

screen steam_upload_uploading:
    timer 0.1 action SteamUploader_Execute
    frame:
        xysize (1.0, 1.0)
        frame:
            xysize (0.7, 0.7)
            align (0.5, 0.5)
            vbox:
                spacing 50
                align (0.5, 0.5)
                label uploading_message:
                    align (0.5, 0.5)
                if not is_running:
                    button:
                        background Solid("222")
                        hover_background Solid("225e")
                        xysize (250, 50)
                        margin (0,0)
                        padding (0,0)
                        align (0.5, 0.8)
                        action Hide("steam_upload_uploading")
                        text "Close":
                            size 20
                            color "fff"
                            align (0.5, 0.5)
                            text_align 0.5
