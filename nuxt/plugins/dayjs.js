import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import customParseFormat from 'dayjs/plugin/customParseFormat'

dayjs.extend(customParseFormat)
dayjs.locale('fr')

export default (_, inject) => {
  inject('dayjs', dayjs)
}
