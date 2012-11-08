# -*- encoding:utf-8 -*-
import os,re,locale
import subprocess
import sublime, sublime_plugin
import thread,functools

locale.setlocale(locale.LC_CTYPE,"en_US.UTF-8")
OCTOPRESS_METHOD_NEW_POST = 1
OCTOPRESS_METHOD_NEW_PAGE = 2
OCTOPRESS_METHOD_GENERATE = 3
OCTOPRESS_METHOD_DEPLOY = 4
OCTOPRESS_METHOD_GEN_DEP = 5
class OctotoolsCommand(sublime_plugin.WindowCommand):
	def run_command(self,command,method_type):
		exec_command = self.command + " " + command
		os.chdir(self.octo_path)
		self.method = method_type
		self.proc = subprocess.Popen(exec_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,env=self.env, shell=True)
		thread.start_new_thread(self.check_result,())

	def check_result(self):
		sublime.set_timeout(functools.partial(self.show_status, "finish"), 0)
		self.output = self.proc.stdout.read().strip()
		sublime.set_timeout(functools.partial(self.finish), 5)

	def finish(self):
		if self.method == OCTOPRESS_METHOD_NEW_POST :
			if re.search('Creating new post: ',self.output):
				self.file =  self.output.split(": ")[1]
				self.window.open_file(os.path.join(self.octo_path,self.file))
			else:
				sublime.error_message("can't rake new post, error info:\n %s "%output)
				return False
		elif self.method == OCTOPRESS_METHOD_GENERATE :
			if re.search('Successfully generated site',self.output):
				sublime.message_dialog("generate blog is success!")
		elif self.method == OCTOPRESS_METHOD_DEPLOY or \
		 self.method == OCTOPRESS_METHOD_GEN_DEP :
			if re.search('OK',self.output):
				sublime.message_dialog("deploy post is success!")
	def show_status(self,text):
		sublime.status_message(text)
	# def post_new(self,output):

	# def post_page(self,output):

	def load_config(self):
		config = sublime.load_settings("octotools.sublime-settings")
		octo_path = config.get('octoblog_path')
		rake_env = config.get('rbenv_shims_path')
		self.command = "rake"
		self.env = os.environ.copy()
		self.env['LC_CTYPE'] ='en_US.UTF-8'
		self.env['LANG'] = 'en_US.UTF-8'
		if octo_path != None and os.path.exists(octo_path) :
			self.octo_path = octo_path
			if rake_env != None and os.path.isdir(rake_env) :
				self.env['PATH'] =  rake_env + ':' +  self.env['PATH']
			sublime.status_message("loading config ...")
			return True
		else:
			#self.error_message("not find octopress path ")
			if sublime.ok_cancel_dialog("not find octopress,would you like write it?"):
				self.window.open_file("octotools.sublime-settings")
			else:
				sublime.message_dialog("Please set your octopress when next use it.")
			return False
class OctotoolsNewPostCommand(OctotoolsCommand):
	def run(self):
		if not self.load_config(): 
			return False
		self.window.show_input_panel("Enter Title Of New Post", "", self.on_done, None, None)
	def on_done(self,text):
		#sublime.message_dialog(text)
		command = "new_post\['%s'\]" % text
		self.run_command(command, OCTOPRESS_METHOD_NEW_POST)
class OctotoolsGenerateCommand(OctotoolsCommand):
	def run(self):
		if not self.load_config(): 
			return False
		command = "generate"
		self.run_command(command,OCTOPRESS_METHOD_GENERATE)
class OctotoolsDeployCommand(OctotoolsCommand):
	def run(self):
		if not self.load_config(): 
			return False
		command = "deploy"
		self.run_command(command,OCTOPRESS_METHOD_DEPLOY)

class OctotoolsGenDeployCommand(OctotoolsCommand):
	def run(self):
		if not self.load_config():
			return False
		command = "gen_deploy"
		self.run_command(command,OCTOPRESS_METHOD_GEN_DEP)