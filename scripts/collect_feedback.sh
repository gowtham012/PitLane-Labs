echo 'Query: '
read Q
echo 'Response: '
read R
echo 'Rating (1-5): '
read rating
echo 'Correction (optional): '
read C
python - <<EOF
from agent.feedback_loop import log_feedback
log_feedback("$Q","$R",$rating,"$C")
EOF