# CHART TYPES
.mark_bar(
    title='Title to show'
)
.mark_point()

# ENCODINGS
y=alt.Y('Field',
    sort=['-x', 'ascending', 'descending', '[]'],
    title='Axis title to show',
    axis=alt.Axis(),
    scale=alt.Scale(),
)
x=alt.X() # Same
color=alt.Color(
    legend=alt.Legend()
)
column=alt.Column()
row=alt.Row()
shape=alt.Shape('Field',
                legend=alt.Legend()
                )
color=alt.Color('Field',
                legend=alt.Legend()
                )

# OPTIONS FOR ENCODINGS
alt.Axis(
    labels=[True, False],
    orient=['top', 'bottom', 'left', 'right'],
    format= 'format of numbers, e.g. d for integer'
)
alt.Scale(
    domain=(min, max)
)
alt.Legend(
    title='Legend Title',
    values=['Values'],
    orient=['none', 'left', 'right', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
)
