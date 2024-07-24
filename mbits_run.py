# script to run testbenches
# import dependencies
import argparse
import os

def findModuleName(filename):
    stop_index = filename.find(".")
    module_name = filename[:stop_index]
    return module_name
'''
vlog -sv \
	+acc \
	+cover \
	+fcover \
	-l axi4_compile.log \
	-f ../axi_compile.f 
vsim -vopt \
	work.axi_master_top \
	-voptargs=+acc=npr \
	-assertdebug \
	+UVM_TESTNAME=$(test) \
	+UVM_VERBOSITY=$(uvm_verbosity) \
	-l $(test_folder)/$(test).log \
	-sva \
  -coverage \
	-c -do "log -r /*; add wave -r /*; coverage save -onexit -assert -directive -cvg -codeAll $(test_folder)/$(test)_coverage.ucdb; run -all; exit" \
	-wlf $(test_folder)/waveform.wlf
	wlf2vcd -o $(test_folder)/waveform.vcd $(test_folder)/waveform.wlf 
'''    
def vsim(content, cov_en, dump_en, module_name, test, verbosity):
    if(cov_en & dump_en):
        new_content=f"""
mkdir test
vsim -vopt work.{module_name} -voptargs=+acc=npr -assertdebug +UVM_TESTNAME={test} +UVM_VERBOSITY={verbosity} -l {test}/{test}.log -sva -coverage -c -do "log -r /*; add wave -r /*; coverage save -onexit -aser -directive -cvg -codeAll {test}/{test}_coverage.ucdb; run -all; exit" -wlf {test}/{test}_wave.wlf
wlf2vcd -o {test}/{test}_wave.vcd {test}/{test}_wave.wlf
vcover report -html {test}{test}_coverage.ucdb -htmldir {test}/cov_report -details"""
        content=content+new_content
    elif(cov_en):
        new_content=f"""
mkdir test
vsim -vopt work.{module_name} -voptargs=+acc=npr -assertdebug +UVM_TESTNAME={test} +UVM_VERBOSITY={verbosity} -l {test}/{test}.log -sva -coverage -c -do "log -r /*; add wave -r /*; coverage save -onexit -aser -directive -cvg -codeAll {test}/{test}_coverage.ucdb; run -all; exit"
vcover report -html {test}{test}_coverage.ucdb -htmldir {test}/cov_report -details"""
        content=content+new_content
    elif(dump_en):
        new_content=f"""
mkdir test
vsim -vopt work.{module_name} -voptargs=+acc=npr -assertdebug +UVM_TESTNAME={test} +UVM_VERBOSITY={verbosity} -l {test}/{test}.log -sva -c -do "log -r /*; add wave -r /*; run -all; exit" -wlf {test}/{test}_wave.wlf
wlf2vcd -o {test}/{test}_wave.vcd {test}/{test}_wave.wlf"""
        content=content+new_content
    else:
        new_content=f"""
mkdir test
vsim -vopt work.{module_name} -voptargs=+acc=npr +UVM_TESTNAME={test} +UVM_VERBOSITY={verbosity} -l {test}/{test}.log -c -do "run -all; exit" """
        content=content+new_content
    return content
def vlog(content, cov_en, top_tb_file_name, module_name):
    if(cov_en):
        new_content=f"""
vlog {top_tb_file_name} +acc +cover +fcover -l {module_name}.log"""
    else:
        new_content=f"""
vlog {top_tb_file_name} +acc -l {module_name}.log"""
    content=content+new_content
    return content

def vlib(content):
    new_content="""vlib work"""
    content=content+new_content
    return content

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("TB_name", nargs="?", type=str,help="Name of the testBench file")
parser.add_argument("-c", "--coverage", action="store_true",help="Include coverage")
parser.add_argument("-d", "--dump", action="store_true",help="Include Waveform")
parser.add_argument("-f", "--filter", nargs="?", type=str, help="Add Filter")
parser.add_argument("-v", "--verbosity", nargs="?", type=str, help="Define UVM Verbosity")
parser.add_argument("-t", "--test", nargs="?", type=str, help="testcase name")

args = parser.parse_args()

top_tb_file_name=str(args.TB_name)
cov_en=bool(args.coverage)
dump_en=bool(args.dump)
test_filter=str(args.filter)
test=str(args.test)
verbosity=str(args.verbosity)
if test  =="None":
    test = "base_test"
if verbosity == "None":
    verbosity = "UVM_MEDIUM"
module_name=findModuleName(top_tb_file_name)

command_file = "commands.sh"
content = """#!/bin/bash
"""
content=vlib(content)
content=vlog(content,cov_en,top_tb_file_name,module_name)
content=vsim(content,cov_en,dump_en,module_name,test,verbosity)

with open(command_file, "w") as f:
    f.write(content)
os.system("bash commands.sh")
