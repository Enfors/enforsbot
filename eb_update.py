"Makes it possible to update code without restarting."

import imp, sys

class Update(object):
    def __init__(self):
        self.modules = {}
        self.objects = {}

    def request_obj(self, module_path, class_name, args=None):
        "Load and return requested object, if not already cached."
        # Remove trailing .py, if present
        if module_path[-3:] == ".py":
            module_path = module_path[:-3]

        # Check if the module has been loaded
        if module_path not in self.modules:
            # todo: handle exceptions here

            # The module hasn't been loaded yet. Load it now.
            mod = __import__("eb_cmd." + module_path)

            self.modules[module_path] = mod
            self.objects[module_path] = {}
        else:
            # Module already loaded. Retrieve it from cache.
            mod = self.modules[module_path]

        # Check if the object is loaded.
        if class_name not in self.objects[module_path]:
            # The object is not loaded. Load it now.

            if args:
                class_path = "mod.%s.%s(args)" % (module_path, class_name)
                print("1")
            else:
                class_path = "mod.%s.%s()" % (module_path, class_name)
                print("module_path: %s" % module_path)
                print("class_name : %s" % class_name)
            print("Evaluating: '%s'" % class_path)
            self.objects[module_path][class_name] = eval(class_path)

        return self.objects[module_path][class_name]

    def reload_module(self, module_path):
        "Reload a module that was changed since last time it was loaded."
        print("[Update] Reloading %s." % module_path)

        if not module_path in self.modules:
            print("[Update] Module not loaded.")
            print("Modules: %s" % self.modules)
            return False

        imp.reload(sys.modules[module_path])

        self.objects[module_path] = { }

        return True

update = Update()
