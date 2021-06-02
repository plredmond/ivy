
import ivy_init
import sys
import json
import platform
import os
import string
import time

def usage():
    print "usage: \n {} {{option=value...}} <file>.dsc".format(sys.argv[0])
    sys.exit(1)

next_unused_port = 49123

def get_unused_port(protocol):
    global next_unused_port
    next_unused_port += 1
    return next_unused_port

def lookup_ip_addr(hostname):
    return '0x7f000001'

def run_in_terminal(cmd,name):
    # if platform.system() == 'Darwin':
    #     from applescript import tell
    #     term_cmd = cmd.replace('"','\\"')
    #     tell.app( 'Terminal', 'do script "' + term_cmd + '"')
    xcmd = "xterm -T '{}' -e '{}'&\n".format(name,cmd+'; read -p "--press enter--"')
    print xcmd
    os.system(xcmd)
    
def read_params():
    ps = dict()
    args = sys.argv[1:]
    while args and '=' in args[0]:
        thing = string.split(args[0],'=')
        if len(thing) > 2:
            usage()
        ps[thing[0]] = thing[1]
        args = args[1:]
    sys.argv = sys.argv[0:1] + args
    return ps

def main():
    ps = read_params()
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    dscfname = sys.argv[1]
    try:
        with open(dscfname) as inp:
            try:
                descriptor = json.load(inp)
            except json.JSONDecodeError as err:
                sys.stderr.write("error in {}: {}".format(dscfname,err.msg))
                sys.exit(1)
    except:
        sys.stderr.write('not found: {}\n'.format(dscfname))
        sys.exit(1)

    hosts = {}
    processes = descriptor['processes']
    for process in processes:
        hosts[process['name']] = 'localhost'

    param_vals = {}

    legal_params = set(p['name'] for p in processes)
    legal_params.update(set(prm['name'] for p in processes for prm in p['params']))
    print legal_params
    for prm in ps:
        if prm not in legal_params:
            print "unknown parameter: {}".format(prm)
            exit(1)
    
    def get_process_dimensions(process):
        pname = process['name']
        if pname in ps:
            try:
                dim = eval(ps[pname],{},{})
            except:
                print "bad argument: {}={}".format(pname,ps[pname])
                exit(1)
            dim = [x if isinstance(x,list) else [x] for x in dim]
        else:
            dim = [[]]
        return dim
    
    for process in processes:
        pname = process['name']
        dim = get_process_dimensions(process)
        pparms = process['indices']
        if not all(len(d) == len(pparms) for d in dim):
            print "wrong number of parameters in instance list for process {}".format(pname)
        for param in process['params']:
            if param['type'].endswith('udp.endpoint'):
                if param['name'].startswith(pname+'.') or pname == 'extract' or pname == 'this':
                    ids = []
                    for d in dim:
                        port = get_unused_port('udp')
                        id = '{{addr:{},port:{}}}'.format(lookup_ip_addr(hosts[pname]),port)
                        ids.append(id)
                    if param['name'] in param_vals:
                        sys.stderr.write("endpoint {} is used by multiple processes".format(param['name']))
                        sys.exit(1)
                    param_vals[param['name']] = '"{}"'.format(ids[0] if len(pparms) == 0 else ('[' + ','.join('[' + ','.join(map(str,d)) + ',' + id + ']' for d,id in zip(dim,ids)) + ']'))
                    
        ps.update(param_vals)

    for process in processes:
        dim = get_process_dimensions(process)
        for d in dim:
            binary = process['binary']
            cmd = [binary if '/' in binary else './' + binary]
            psc = ps.copy()
            for p,v in zip(process['indices'],d):
                psc[p['name']] = str(v)
            for param in process['params']:
                if param['name'] in psc:
                    val = psc[param['name']]
                    if 'default' in param:
                        cmd.append('{}={}'.format(param['name'],val))
                    else:
                        cmd.append('{}'.format(val))
            print ' '.join(cmd)
            wname = process['name'] + ('('+','.join(map(str,d))+')' if d else '')
            run_in_terminal(' '.join(cmd),wname)
            time.sleep(0.5)
            
        
if __name__ == "__main__":
    main()
