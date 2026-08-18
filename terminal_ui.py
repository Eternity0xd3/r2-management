from r2_management.r2_management import R2Management
import os

from dotenv import load_dotenv
from colorama import Fore, init    

OPERATION_MAPPING = {
    1: "upload",
    2: "download",
    3: "list",
    4: "delete",
    5: "exit"
}

# enum for UI state
SELECTING_OPERATION = 0
INPUTTING_ARGUMENT = 1
COMFIRMING_OPERATION = 2
OPERATE = 3

def create_default_state():
    return {
        "step": SELECTING_OPERATION,
        "operation": None,
        "argument_number": None,
        "user_argument": [],
    }

def ui_init():
    init()
    
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def run_operation(r2, operation, args):
    if operation == 1:
        obj_link = r2.upload(args[0],args[1])
        return f"The image is uploaded to {obj_link}"
    if operation == 2:
        image_path = r2.download(args[0],args[1])
        return f"The image is downloaded to {image_path}"
    if operation == 3:
        return r2.list()
    if operation == 4:
        r2.delete(args[0])
        return f"{args[0]} is deleted"
    

def get_argument_name(operation):
    args_name = []
    if operation == 1:
        args_name = ["file_path", "object_name"]
    elif operation == 2:
        args_name = ["object_name", "file_path"]
    elif operation == 4:
        args_name = ["object_name"]
    return args_name

def render_ui(state):
    clear_screen()
    step = state["step"]
    operation = state["operation"]
    argument_number = state["argument_number"]
    user_argument = state["user_argument"]

    if step >= SELECTING_OPERATION:
        # determine display color
        colors = []
        for i in range(1,6,1):
            if(operation and operation == i):
                colors.append(Fore.GREEN)
            else:
                colors.append(Fore.YELLOW)

        # output
        print(Fore.WHITE + "Select an operation:")
        print(colors[0] + "1. Upload file")
        print(colors[1] + "2. Download file")
        print(colors[2] + "3. List file")
        print(colors[3] + "4. Delete file")
        print(colors[4] + "5. Exit")
        print("")

    if step >= INPUTTING_ARGUMENT and operation in [1, 2, 4]:
        # decide the argument names on display
        args_name = get_argument_name(operation)

        colors = []
        # decide the color
        for i in range(len(args_name)):
            if i == argument_number and step == INPUTTING_ARGUMENT:
                colors.append(Fore.GREEN)
            else:
                colors.append(Fore.YELLOW)

        # output
        print(Fore.WHITE + "required arguments:")
        for i in range(len(args_name)):
            print(colors[i] + args_name[i])
        print("")

    if step == COMFIRMING_OPERATION and operation in [4]:
        print(Fore.WHITE + f"Are you sure to operate: {OPERATION_MAPPING[operation]}({", ".join(user_argument)})")


def application(r2):
    ui_init()
    state = create_default_state()
    while True:
        next_state = state
        step = state["step"]
        operation = state["operation"]
        argument_number = state["argument_number"]
        user_argument = state["user_argument"]

        if(operation == 5):
            break

        render_ui(state)

        if step == SELECTING_OPERATION:
            print("")
            selected_operation = input(Fore.WHITE + "Please select the operation: ")
            if(selected_operation not in ["1","2","3","4","5"]):
                raise ValueError("Invalid input")
            selected_operation = int(selected_operation)
            selected_operation_arguments = get_argument_name(selected_operation)
            if len(selected_operation_arguments) >= 1:
                next_state["step"] = INPUTTING_ARGUMENT
                next_state["argument_number"] = 0
            else:
                next_state["step"] = OPERATE
            next_state["operation"] = selected_operation
        if step == INPUTTING_ARGUMENT:
            print("")
            arg = input(Fore.WHITE + f"please input the {get_argument_name(operation)[argument_number]}: ")
            next_state["user_argument"].append(arg)
            has_next_arg = argument_number + 1 < len(get_argument_name(operation))
            if(has_next_arg):
                next_state["argument_number"] += 1
            else:
                if operation in [4]:
                    next_state["step"] = COMFIRMING_OPERATION
                else:
                    next_state["step"] = OPERATE
        if step == COMFIRMING_OPERATION:
            print("")
            arg = input(Fore.WHITE + "y/n: ")
            if arg.lower() == "y":
                next_state["step"] = OPERATE
            else:
                print(Fore.YELLOW + "canceled")
                os.system("pause")
                next_state = create_default_state()
        if step == OPERATE:
            print(Fore.WHITE + f"operating: {OPERATION_MAPPING[operation]}({", ".join(user_argument)})")
            output = run_operation(r2, operation, user_argument)
            print(output)
            os.system("pause")
            next_state = create_default_state()

        state = next_state

def throw_error(error):
    print("\n" + Fore.RED + "Unexpected error: " + str(error) + Fore.WHITE)

def start_app(r2):
    try:
        application(r2)
    except Exception as e:
        throw_error(e)
    

if __name__ == "__main__":
    load_dotenv()   
    r2_management = R2Management(
        bucket_name=os.getenv("BUCKET"),
        endpoint_url=os.getenv("ENDPOINT"),
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_ACCESS_KEY"),
        public_url=os.getenv("PUBLIC_URL")
    )

    start_app(r2_management)
