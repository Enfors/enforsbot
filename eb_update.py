"Makes it possible to update code without restarting."

import imp, sys

class Update(object):
    def __init__(self):
        self.modules = { }
        self.objects = { }

    def request_obj(self, module_path, class_name, args = None):
        # Remove trailing .py, if present
        if module_path[-3:] == ".py":
            module_path = module_path[:-3]

        # Check if the module has been loaded
        if not module_path in self_modules:
            # todo: handle exceptions here

            # The module hasn't been loaded yet. Load it now.
            mod = __import__(module_path)

            self.modules[module_path] = mod
            self.objects[module_path] = { }
        else:
            # Module already loaded. Retrieve it from cache.
            mod = self.modules[module_path]

        # Check if the object is loaded.
        if not class_name in self.objects[module_path]:
            # The object is not loaded. Load it now.

            if args:
                class_path = "mod.%s.%s(args)" % (module_path, class_name)
            else:
                class_path = "mod.%s.%s()" % (module_path, class_name)
            self.objects[module_path][class_name] = eval(class_path)

        return self.objects[module_path][class_name]

    def reload_module(self, module_path):
        print("[Update] Reloading %s." % module_path)

        if not module_path in self.modules:
            print("[Update] Module not loaded.")
            print("Modules: %s" % self.modules)
            return False

        imp.reload(sys.modules[module_path])

        self.objects[module_path] = { }

        return True

update = Update()
