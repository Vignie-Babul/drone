#!/bin/bash


cat << 'EOF' > fix_ruff_final.py
import re

with open('main.py', 'r') as f:
    main_code = f.read()

main_code = main_code.replace(
    "self.drone_ctrl = DroneController(self.drone_root, self.drone_tilt, self.propellers, self.drone_config, self.vr_sim)",
    "self.drone_ctrl = DroneController(\n            self.drone_root, self.drone_tilt, self.propellers, self.drone_config, self.vr_sim\n        )"
)

with open('main.py', 'w') as f:
    f.write(main_code)


with open('src/drone_controller.py', 'r') as f:
    drone_code = f.read()

pattern = r"if parent:\s*up_vec = parent\.getRelativeVector\(self\.tilt_node, Vec3\(0, 0, 1\)\)\s*else:\s*up_vec = Vec3\(0, 0, 1\)"
replacement = "up_vec = parent.getRelativeVector(self.tilt_node, Vec3(0, 0, 1)) if parent else Vec3(0, 0, 1)"

drone_code = re.sub(pattern, replacement, drone_code)

with open('src/drone_controller.py', 'w') as f:
    f.write(drone_code)
EOF

python3 fix_ruff_final.py
rm fix_ruff_final.py
