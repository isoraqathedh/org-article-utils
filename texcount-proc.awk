BEGIN {
    part = 0
    chapter = 0
}
/Part:/ {
    ++part
}
/Chapter:/ {
    gsub(/^[^:]+: /, "", $2)
    print part, ++chapter, $1, "\"" $2 "\""
}
