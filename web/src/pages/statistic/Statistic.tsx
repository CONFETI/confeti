import React, { useState } from 'react'
import { Box, TextField } from '@material-ui/core'
import Autocomplete from '@material-ui/lab/Autocomplete/Autocomplete'
import { ChartType, IStatisticOption } from 'types'
import { LanguageStatistics } from './components/LanguageStatistics'
import { useStyles } from './styles'
import { TagStatistics } from './components/TagStatistics'

interface StatisticProps {}

enum StatisticName {
  LANGUAGE_STATISTICS = 'Language statistics',
  TAG_STATISTICS = 'Tag statistics'
}

const statisticOptions = [
  {
    name: StatisticName.LANGUAGE_STATISTICS,
    chartType: ChartType.PIE
  },
  {
    name: StatisticName.TAG_STATISTICS,
    chartType: ChartType.PIE
  }
] as IStatisticOption[]

const Statistic = () => {
  const classes = useStyles()
  const [statisticOption, setStatisticOption] = useState<IStatisticOption>(statisticOptions[0])

  return (
    <Box>
      <Box className={classes.tools}>
        <Autocomplete
          id="statistic-chart-select"
          className={classes.statisticSelect}
          options={statisticOptions}
          getOptionLabel={(option: IStatisticOption) => `${option.name}`}
          filterSelectedOptions
          value={statisticOption}
          onChange={(_, value: IStatisticOption, reason) => {
            if (reason === 'select-option' && value) {
              setStatisticOption(value)
            }
          }}
          renderInput={params => (
            <TextField
              {...params}
              InputProps={{
                ...params.InputProps,
                classes: {
                  input: classes.statisticTextField
                }
              }}
              color="secondary"
              placeholder="Choose a statistic"
            />
          )}
        />
        {statisticOption.name === StatisticName.LANGUAGE_STATISTICS && (
          <LanguageStatistics defaultChartType={statisticOption.chartType} />
        )}
        {statisticOption.name === StatisticName.TAG_STATISTICS && (
          <TagStatistics defaultChartType={statisticOption.chartType} />
        )}
      </Box>
    </Box>
  )
}

export default Statistic
