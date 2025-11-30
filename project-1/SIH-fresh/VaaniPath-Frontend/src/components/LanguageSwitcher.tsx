import { useTranslation } from 'react-i18next';
import { INDIAN_LANGUAGES } from '@/constants/languages';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Globe } from 'lucide-react';

interface LanguageSwitcherProps {
    variant?: 'dropdown' | 'list';
}

export const LanguageSwitcher = ({ variant = 'dropdown' }: LanguageSwitcherProps) => {
    const { i18n } = useTranslation();

    const changeLanguage = (langCode: string) => {
        i18n.changeLanguage(langCode);
        localStorage.setItem('i18nextLng', langCode);
    };

    if (variant === 'list') {
        return (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {INDIAN_LANGUAGES.map((lang) => (
                    <button
                        key={lang.code}
                        onClick={() => changeLanguage(lang.code)}
                        className={`flex flex-col items-center justify-center p-4 rounded-lg border transition-all ${i18n.language === lang.code
                                ? 'border-primary bg-primary/5'
                                : 'border-border hover:border-primary/50'
                            }`}
                    >
                        <span className="text-lg font-bold mb-1">{lang.native}</span>
                        <span className="text-sm text-muted-foreground">{lang.name}</span>
                    </button>
                ))}
            </div>
        );
    }

    return (
        <Select value={i18n.language} onValueChange={changeLanguage}>
            <SelectTrigger className="w-[140px] md:w-[180px]">
                <Globe className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Select Language" />
            </SelectTrigger>
            <SelectContent className="max-h-[300px]">
                {INDIAN_LANGUAGES.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                        <span className="flex items-center">
                            <span className="mr-2">{lang.native}</span>
                            <span className="text-muted-foreground text-xs">({lang.name})</span>
                        </span>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
};
