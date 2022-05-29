class ParallelCommandsTracker:
    __started_commands = {}
    __commands_integer_mapping = {}

    def command_count(self):
        return len(self.__started_commands)

    def add_command(self, tid, timestamp, cmd):
        if cmd not in self.__commands_integer_mapping:
            # zero is reserved
            self.__commands_integer_mapping[cmd] = len(
                self.__commands_integer_mapping
            ) + 1
        self.__started_commands[tid] = {
            "receivedAt": timestamp,
            "respondedAt": None,
            "cmd": self.__commands_integer_mapping[cmd],
            "parallelCommandsStart": self.command_count(),
            "parallelCommandsEnd": 0,
            "parallelCommandsFinished": 0,
            "firstParallelCommandStart": self.__get_first_started_command(),
            "firstParallelCommandFinished": None,
            "listParallelCommandsStart": self.__get_list_parallel_commands_start(),
            "listParallelCommandsFinished": {}
        }

    def __get_list_parallel_commands_start(self):
        started_command_list = {}
        for key, value in self.__started_commands.items():
            cmd = value["cmd"]
            if cmd in started_command_list:
                started_command_list[cmd] = started_command_list[cmd] + 1
            else:
                started_command_list[cmd] = 1
        return started_command_list

    def __get_first_started_command(self):
        first_command_tid = None
        for key, value in self.__started_commands.items():
            if first_command_tid is None:
                first_command_tid = key
            time_delta = (
                    value["receivedAt"]
                    - self.__started_commands[first_command_tid]["receivedAt"]
            )
            if time_delta.total_seconds() > 0:
                first_command_tid = key

        first_command_request_type = None
        if first_command_tid is not None:
            first_command_request_type = \
                self.__started_commands[first_command_tid][
                    "cmd"
                ]
        return first_command_request_type

    def remove_command(self, tid):
        # pop command
        cmd = self.__started_commands[tid]["cmd"]
        self.__started_commands.pop(tid)
        self.__add_finished_command_to_list_parallel_commands_finished(cmd)

        for key in self.__started_commands.keys():
            # set first finished command if none present
            if self.__started_commands[key][
                "firstParallelCommandFinished"] is None:
                self.__started_commands[key][
                    "firstParallelCommandFinished"] = cmd
            # increment parallel finished for all current commands
            self.__started_commands[key]["parallelCommandsFinished"] = (
                    self.__started_commands[key]["parallelCommandsFinished"] + 1
            )

    def __add_finished_command_to_list_parallel_commands_finished(self, cmd):
        for key, value in self.__started_commands.items():
            if cmd in value["listParallelCommandsFinished"]:
                value["listParallelCommandsFinished"][cmd] = \
                    value["listParallelCommandsFinished"][cmd] + 1
            else:
                value["listParallelCommandsFinished"][cmd] = 1

    def get_command(self, tid):
        pass

    def __contains__(self, item):
        return item in self.__started_commands

    def __getitem__(self, item):
        return self.__started_commands[item]

    def __setitem__(self, key, value):
        self.__started_commands[key] = value

    def items(self):
        return self.__started_commands.items()

    def reset(self):
        self.__started_commands.clear()

    def __str__(self):
        return str(self.__started_commands)

    def get_command_mapping(self):
        return self.__commands_integer_mapping
