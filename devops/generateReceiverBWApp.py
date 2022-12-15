import argparse
import sys
import os
import shutil
import glob
import time
import re

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--app_ident", dest="app_ident", help="the id in the endpoint record unique to this interface listener")
parser.add_argument("-i", "--input", dest="tmpl_location", help="the directory of the receiver template application")
parser.add_argument("-o", "--output", dest="app_out_location", help="the directory to output the renamed package")
parser.add_argument("-p", "--port", dest="port", help="if you want to set the LLP Port on generation")
parser.add_argument("-d", "--host", dest="host", help="if you want to set the LLP Host on generation")
args = parser.parse_args(sys.argv[1:])


def generateReceiverBWApp(args):
    print('Generating Receiver Endpoint Application')
    receiver = "c:/OASIS/bw_workspace/translation_engine/template.receiver"
    receiver_app = "c:/OASIS/bw_workspace/translation_engine/template.receiver.application"
    output_dir = "c:/OASIS/bw_workspace/endpoint_apps/"
    receiver_out = args.app_ident+'.receiver'
    receiver_app_out = args.app_ident+'.receiver.application'
    if args.tmpl_location is not None:
        receiver = os.path.join(args.tmpl_location, "template.receiver")
        receiver_app = os.path.join(args.tmpl_location, "template.receiver.application")
    if args.app_out_location is not None:
        output_dir = args.app_out_location
    # lets copy the folder with new name

    n_rec_path = os.path.join(output_dir, receiver_out)
    n_rec_app_path = os.path.join(output_dir, receiver_app_out)

    if os.path.exists(n_rec_path):
        shutil.rmtree(n_rec_path)
    if os.path.exists(n_rec_app_path):
        shutil.rmtree(n_rec_app_path)
    print('Copying '+receiver+' to '+n_rec_path)
    shutil.copytree(receiver, n_rec_path)
    print('Copying '+receiver_app+' to '+n_rec_app_path)
    shutil.copytree(receiver_app, n_rec_app_path)
    # lets pause after copy before mods just cause I was seeing some missed mods and copying on windows
    time.sleep(5)
    # rename iml file
    print('rename '+os.path.join(n_rec_path,'template.receiver.iml')+' to '+os.path.join(n_rec_path, args.app_ident+'.receiver.iml'))
    shutil.move(os.path.join(n_rec_path,'template.receiver.iml'), os.path.join(n_rec_path, args.app_ident+'.receiver.iml'))

    print('Edit build.properties')
    # edit build.properties
    with open(os.path.join(n_rec_path,'newbuild.properties'), 'w') as nb:
        with open(os.path.join(n_rec_path,'build.properties')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('template.receiver.iml', args.app_ident+'.receiver.iml'))
    os.remove(os.path.join(n_rec_path, 'build.properties'))
    shutil.move(os.path.join(n_rec_path, 'newbuild.properties'), os.path.join(n_rec_path,'build.properties'))

    print('Edit .project')
    # change .project name
    with open(os.path.join(n_rec_path, '.newproject'), 'w') as nb:
        with open(os.path.join(n_rec_path, '.project')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<name>template.receiver</name>', '<name>'+args.app_ident+'.receiver</name>'))
    os.remove(os.path.join(n_rec_path, '.project'))
    shutil.move(os.path.join(n_rec_path, '.newproject'), os.path.join(n_rec_path, '.project'))
    
    print('Edit manifest')
    # edit manifest
    with open(os.path.join(n_rec_path, 'META-INF', 'NEWMANIFEST.MF'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('template.receiver', args.app_ident+'.receiver'))
    os.remove(os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF'))
    shutil.move(os.path.join(n_rec_path, 'META-INF', 'NEWMANIFEST.MF'), os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF'))

    # need to change META-INF/module.bwm, and the processes sub dirs folder, Activator.bwp, and Outbound.bwp to update the getendpointconfig proc name with package
    print('Editing module.bwm to set unique package/process names')
    with open(os.path.join(n_rec_path, 'META-INF', 'newmodule.bwm'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'META-INF', 'module.bwm')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('processName="oasis.receiver.ReceiveHL7"', 'processName="oasis.'+args.app_ident+'.receiver.ReceiveHL7"')
                line = line.replace('processName="template.receiver.Activator"', 'processName="template.'+args.app_ident+'.receiver.Activator"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'META-INF', 'module.bwm'))
    shutil.move(os.path.join(n_rec_path, 'META-INF', 'newmodule.bwm'), os.path.join(n_rec_path, 'META-INF', 'module.bwm'))

    # rename process sub dirs
    print('renaming Process sub directory package')
    shutil.move(os.path.join(n_rec_path, 'Processes', 'oasis', 'receiver'),
                os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'template', 'receiver'),
                os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver'))

    # rename reference in Activator.bwp
    print('Updating Activator process name package')
    with open(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver', 'newActivator.bwp'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver', 'Activator.bwp')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('name="template.receiver.Activator"', 'name="template.'+args.app_ident+'.receiver.Activator"')
                # Unlike outbound this reference doesn't change cause it is a shared module reference right now
                # line = line.replace('subProcessName="oasis.hl7.receiver.getEndpointConfig"',
                #                     'subProcessName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver', 'Activator.bwp'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver', 'newActivator.bwp'),
                os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.receiver', 'Activator.bwp'))

    # rename reference in ReceiveHL7.bwp
    print('Updating ReceiveHL7 process package name')
    with open(os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver', 'newReceiveHL7.bwp'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver', 'ReceiveHL7.bwp')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('name="oasis.receiver.ReceiveHL7"', 'name="oasis.'+args.app_ident+'.receiver.ReceiveHL7"')
                # Unlike outbound this reference doesn't change cause it is a shared module reference right now
                # line = line.replace('subProcessName="org.carenet.oasis.hl7.outbound.getEndpointConfig"',
                #                     'subProcessName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver', 'ReceiveHL7.bwp'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver', 'newReceiveHL7.bwp'),
                os.path.join(n_rec_path, 'Processes', 'oasis', args.app_ident+'.receiver', 'ReceiveHL7.bwp'))

    print('Edit .application .project file')
    #rename template app .project name
    with open(os.path.join(n_rec_app_path, '.newproject'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, '.project')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<name>template.receiver.application</name>', '<name>'+args.app_ident+'.receiver.application</name>'))
    os.remove(os.path.join(n_rec_app_path, '.project'))
    shutil.move(os.path.join(n_rec_app_path, '.newproject'), os.path.join(n_rec_app_path, '.project'))
    
    print('Editing: '+os.path.join(n_rec_app_path, '.config'))
    #rename template app .config id
    with open(os.path.join(n_rec_app_path, '.newconfig'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, '.config')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<projectDetails id="template.receiver.application">', '<projectDetails id="'+args.app_ident+'.receiver.application">'))
    os.remove(os.path.join(n_rec_app_path, '.config'))
    shutil.move(os.path.join(n_rec_app_path, '.newconfig'), os.path.join(n_rec_app_path, '.config'))

    print('Editing: '+os.path.join(n_rec_path, '.config'))
    print('Replacing: <projectDetails id="com.example.templatereceiver with: <projectDetails id="com.example.'+re.sub('[^A-Za-z0-9]+', '', args.app_ident.lower())+'receiver">')
    #rename template app .config id
    with open(os.path.join(n_rec_path, '.newconfig'), 'w') as nb:
        with open(os.path.join(n_rec_path, '.config')) as b:
            for line in b.readlines():
                # BW seems to not like the id having upper case or dashes or periods and at some point changes the template to templateoutbound
                # instead of template.outbound so lets search and adjust for what BW wants to start with
                # print(line)
                nb.write(line.replace('<projectDetails id="com.example.templatereceiver">', '<projectDetails id="com.example.'+re.sub('[^A-Za-z0-9]+', '', args.app_ident.lower())+'receiver">'))
    os.remove(os.path.join(n_rec_path, '.config'))
    shutil.move(os.path.join(n_rec_path, '.newconfig'), os.path.join(n_rec_path, '.config'))

    # rename module include
    print('Edit TIBCO.xml file')
    with open(os.path.join(n_rec_app_path, 'META-INF', 'NEWTIBCO.xml'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('template.receiver', args.app_ident+'.receiver'))
    os.remove(os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml'))
    shutil.move(os.path.join(n_rec_app_path, 'META-INF', 'NEWTIBCO.xml'), os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml'))

    # edit app package manifest
    print('Edit .application manifest')
    with open(os.path.join(n_rec_app_path, 'META-INF', 'NEWMANIFEST.MF'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF')) as b:
            for line in b.readlines():
                #print(line)
                nb.write(line.replace('template.receiver', args.app_ident+'.receiver'))
    os.remove(os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF'))
    shutil.move(os.path.join(n_rec_app_path, 'META-INF', 'NEWMANIFEST.MF'), os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF'))

    #get all the profile variable files and loop through changing property names referencing template
    profiles = glob.glob(os.path.join(n_rec_app_path, 'META-INF', '*.substvar'))
    print('Edit the .application profile files properties')
    #print(profiles)
    for p in profiles:
        with open(os.path.join(n_rec_app_path, 'META-INF','tmp.substvar'),'w') as t:
            with open(p) as pi:
                for line in pi.readlines():
                    line = line.replace('template.receiver', args.app_ident+'.receiver')
                    line = line.replace('template.outbound', args.app_ident+'.outbound')
                    line = line.replace('<value>template.bw_process_ident</value>', '<value>'+args.app_ident+'</value>')
                    if args.port is not None:
                        line = line.replace('template.port', args.port)
                    if args.host is not None:
                        line = line.replace('template.host', args.host)
                    t.write(line)
        os.remove(p)
        shutil.move(os.path.join(n_rec_app_path, 'META-INF','tmp.substvar'),p)
    profiles = glob.glob(os.path.join(n_rec_path, 'META-INF', '*.substvar'))
    print('Editing the profile files properties')
    #print(profiles)
    for p in profiles:
        with open(os.path.join(n_rec_path, 'META-INF','tmp.substvar'),'w') as t:
            with open(p) as pi:
                for line in pi.readlines():
                    line = line.replace('template.receiver', args.app_ident+'.receiver')
                    line = line.replace('template.outbound', args.app_ident+'.outbound')
                    line = line.replace('<value>template.bw_process_ident</value>', '<value>'+args.app_ident+'</value>')
                    if args.port is not None:
                        line = line.replace('template.port', args.port)
                    if args.host is not None:
                        line = line.replace('template.host', args.host)
                    t.write(line)
        os.remove(p)
        shutil.move(os.path.join(n_rec_path, 'META-INF','tmp.substvar'),p)

generateReceiverBWApp(args)

