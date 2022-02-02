
# SCP deploy script

# ====================================
# Remote config
REMOTE_USER="ec2-user"
REMOTE_HOST="monkechat.com"
REMOTE_MAP="/var/www/code/bots/disclauncher"
LOCAL_MAP="C:/Users/Nate/Documents/projects/repos/disc-launcher"

# Selection config
IGNORE_DOT_DIRS='true'
IGNORE_DIRS='__pycache__'

# Output
V_SPEC='true'
# ====================================

DIRS=('.git')
# dir_str=$(find -type d)
# for dir in $dir_str; do
#     [[ $dir =~ .*\/\.[^\/]* ]] && DIRS+=($dir)
# done
# for dir in $IGNORE_DIRS; do
#     DIRS+=( "$dir" )
# done

prune=""
dircount=${#DIRS[@]}
if [[ $dircount -gt 0 ]]; then
    if [[ $dircount -gt 1 ]]; then
        prune="-type d ( "
        for dir in ${DIRS[@]}; do
            prune+="-name $dir "
            if [[ $dircount -gt 1 ]]; then
                prune+='-o '
            fi
            dircount=$((dircount-1))
        done
        prune+=") -prune -o"
    else
        prune="-type d -name ${DIRS[0]} -prune -o"
    fi
fi

echo $prune

FILES=$(find . "$prune" -name "*.*" -type f)

echo $FILES

exit 1

printf "\nStarting deploy...\n"
printf "Path local: $LOCAL_MAP/\n"
printf "Path remote: $REMOTE_MAP/\n"
printf "Starting transfer to $REMOTE_USER@$REMOTE_HOST:$REMOTE_MAP/...\n"
idx=0
for file in ${FILES[@]}; do
    printf "[$idx] Transferring $LOCAL_MAP/$file -> $REMOTE_MAP/$file\n"
    scp -i $KEY_LOC -q $LOCAL_MAP/$file $REMOTE_USER@$REMOTE_HOST:$REMOTE_MAP/$file
    idx=$((idx + 1))
done
printf "Finished deploy.\n"

exit 0
