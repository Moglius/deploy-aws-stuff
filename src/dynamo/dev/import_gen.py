from string import Template

d = {"name": "ww", "instance_id": "i-12321fasdas123"}

with open("import.tpl", "r") as template, open("import.tf", "w") as outfile:
    src = Template(template.read())
    mylist = []
    for i in range(4):
        print(i)
        mylist.append(src.substitute(d))

    for imp in mylist:
        outfile.write(f"{imp}\n")
