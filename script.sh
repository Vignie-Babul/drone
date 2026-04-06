#!/bin/bash


cat << 'EOF' > fix_issues.py
with open('main.py', 'r') as f:
    main_code = f.read()

main_code = main_code.replace(
    "self.ground.setPos(0, 0, -1)",
    "self.ground.setPos(-500, -200, -1)"
)

with open('main.py', 'w') as f:
    f.write(main_code)

with open('src/level_manager.py', 'r') as f:
    lm_code = f.read()

lm_code = lm_code.replace(
    "if (drone_pos - ring.getPos()).length() < 4.0:",
    "if (drone_pos - ring.getPos()).length() < 6.5:"
)

with open('src/level_manager.py', 'w') as f:
    f.write(lm_code)
EOF

python3 fix_issues.py
rm fix_issues.py

echo "Трава отцентрована, радиус колец увеличен!"
